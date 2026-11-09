package org.iowo.d4.biblestudy;

import android.app.Activity;
import android.content.*;
import android.net.Uri;
import android.os.Build;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.Base64;
import android.webkit.JavascriptInterface;
import android.widget.Toast;
import androidx.core.content.FileProvider;
import java.io.*;
import java.lang.ref.WeakReference;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** Only explicitly annotated export/clipboard methods are exposed to local JS. */
public final class NativeServices {
    static final int SAVE_DOCUMENT = 7001;
    private static final String KEY_ALIAS = "iowo-d4-device-session-v1";
    private final Context context;
    final ResourceInstaller installer;
    private WeakReference<MainActivity> activity = new WeakReference<>(null);
    private File pendingExport;
    volatile boolean tutorialVisible;

    NativeServices(Context context) {
        this.context = context.getApplicationContext();
        installer = new ResourceInstaller(context);
    }
    void attach(MainActivity current) { activity = new WeakReference<>(current); }

    private SecretKey key() throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore"); store.load(null);
        if (!store.containsAlias(KEY_ALIAS)) {
            KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
            generator.init(new KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE).build());
            return generator.generateKey();
        }
        return (SecretKey) store.getKey(KEY_ALIAS, null);
    }

    public synchronized String readSession() {
        String saved = context.getSharedPreferences("device-vault", Context.MODE_PRIVATE).getString("session", "");
        if (saved.isEmpty()) return "";
        try {
            String[] parts = saved.split("\\.", 2);
            Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
            cipher.init(Cipher.DECRYPT_MODE, key(), new GCMParameterSpec(128, Base64.decode(parts[0], Base64.NO_WRAP)));
            return new String(cipher.doFinal(Base64.decode(parts[1], Base64.NO_WRAP)), StandardCharsets.UTF_8);
        } catch (Exception error) {
            // A reset or unavailable device key requires a new login, never a
            // fallback to saving the password or token without encryption.
            return "";
        }
    }

    public synchronized void writeSession(String json) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key());
        String value = Base64.encodeToString(cipher.getIV(), Base64.NO_WRAP) + "." +
                       Base64.encodeToString(cipher.doFinal(json.getBytes(StandardCharsets.UTF_8)), Base64.NO_WRAP);
        if (!context.getSharedPreferences("device-vault", Context.MODE_PRIVATE).edit().putString("session", value).commit())
            throw new IOException("Could not remember this device's sign-in.");
    }

    public void installResources() throws Exception { installer.install(); }
    public String resourceProgress() { return installer.progress(); }
    public long requiredSetupBytes() throws Exception { return installer.requiredBytes(); }
    public byte[] createPdf(String note) throws Exception { return SermonPdf.create(context, note); }

    public void beginSync(String message) {
        Intent service = new Intent(context, SyncService.class).putExtra("message", message);
        context.startForegroundService(service);
        MainActivity current = activity.get();
        if (current != null) current.runOnUiThread(current::offerNotificationPermission);
    }

    private void onUi(Runnable action) {
        MainActivity current = activity.get();
        if (current != null) current.runOnUiThread(action);
    }

    @JavascriptInterface public boolean tutorialActive() { return tutorialVisible; }
    @JavascriptInterface public void openTutorials() {
        onUi(() -> { MainActivity current=activity.get(); if(current!=null)current.showTutorials(false); });
    }

    @JavascriptInterface public void studyProgress(int percent,String message) {
        if(message==null || message.length()>200) return;
        onUi(() -> { MainActivity current=activity.get(); if(current!=null) current.reportStudyProgress(percent,message); });
    }
    @JavascriptInterface public void studyReady() {
        onUi(() -> { MainActivity current=activity.get(); if(current!=null) current.workspaceReady(); });
    }
    @JavascriptInterface public void studyFailed(String message) {
        onUi(() -> { MainActivity current=activity.get(); if(current!=null) current.startupPreparationFailed(); });
    }

    @JavascriptInterface public void copyText(String text) {
        if (text == null || text.length() > 1024 * 1024) return;
        onUi(() -> ((android.content.ClipboardManager) context.getSystemService(Context.CLIPBOARD_SERVICE))
            .setPrimaryClip(ClipData.newPlainText("Bible Study", text)));
    }

    @JavascriptInterface public void shareText(String text) {
        if (text == null || text.length() > 300000) return;
        onUi(() -> {
            MainActivity current = activity.get(); if (current == null) return;
            Intent share = new Intent(Intent.ACTION_SEND).setType("text/plain").putExtra(Intent.EXTRA_TEXT, text);
            current.startActivity(Intent.createChooser(share, "Share Bible Study"));
        });
    }

    @JavascriptInterface public void exportFile(String encoded, String filename, String type, boolean share) {
        if (encoded == null || encoded.length() > 28 * 1024 * 1024 ||
            !("application/pdf".equals(type) || "application/json".equals(type))) return;
        try {
            byte[] data = Base64.decode(encoded, Base64.DEFAULT);
            if (data.length > 20 * 1024 * 1024) throw new IOException("This export is too large.");
            String safe = (filename == null ? "sermon-notes.pdf" : filename).replaceAll("[^A-Za-z0-9._-]", "_");
            if (safe.length() > 160) safe = safe.substring(0, 160);
            File folder = new File(context.getCacheDir(), "exports"); folder.mkdirs();
            File file = new File(folder, System.currentTimeMillis() + "-" + safe).getCanonicalFile();
            if (!file.getParentFile().equals(folder.getCanonicalFile())) throw new IOException("Invalid export name.");
            try (FileOutputStream output = new FileOutputStream(file)) { output.write(data); }
            final String displayName = safe;
            onUi(() -> {
                MainActivity current = activity.get(); if (current == null) return;
                if (share) {
                    Uri uri = FileProvider.getUriForFile(context, BuildConfig.APPLICATION_ID + ".files", file);
                    Intent intent = new Intent(Intent.ACTION_SEND).setType(type).putExtra(Intent.EXTRA_STREAM, uri)
                        .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                    intent.setClipData(ClipData.newUri(context.getContentResolver(), displayName, uri));
                    current.startActivity(Intent.createChooser(intent, "Share sermon notes"));
                } else {
                    pendingExport = file;
                    Intent intent = new Intent(Intent.ACTION_CREATE_DOCUMENT).setType(type).addCategory(Intent.CATEGORY_OPENABLE)
                        .putExtra(Intent.EXTRA_TITLE, displayName);
                    current.startActivityForResult(intent, SAVE_DOCUMENT);
                }
            });
        } catch (Exception error) {
            onUi(() -> Toast.makeText(context, "The export could not be saved. Your notes are safe; retry Export Notes.", Toast.LENGTH_LONG).show());
        }
    }

    void saveDocumentResult(int result, Uri uri) {
        File source = pendingExport; pendingExport = null;
        if (result != Activity.RESULT_OK || uri == null || source == null) return;
        new Thread(() -> {
            try (InputStream input = new FileInputStream(source); OutputStream output = context.getContentResolver().openOutputStream(uri)) {
                if (output == null) throw new IOException("The selected destination is unavailable.");
                byte[] buffer = new byte[65536]; int count;
                while ((count = input.read(buffer)) != -1) output.write(buffer, 0, count);
                onUi(() -> Toast.makeText(context, "Notes exported", Toast.LENGTH_SHORT).show());
            } catch (Exception error) {
                onUi(() -> Toast.makeText(context, "Could not save to that destination. Retry Export Notes.", Toast.LENGTH_LONG).show());
            }
        }, "save-sermon-export").start();
    }
}
