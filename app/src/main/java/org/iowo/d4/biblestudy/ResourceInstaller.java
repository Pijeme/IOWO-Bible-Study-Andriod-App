package org.iowo.d4.biblestudy;

import android.content.Context;
import android.content.res.AssetManager;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;

/** Streams bundled resources into private storage; no network or website data. */
final class ResourceInstaller {
    private final Context context;
    private final File data;
    private volatile String progress = "{\"completed\":0,\"total\":0,\"message\":\"Preparing library\"}";

    ResourceInstaller(Context context) {
        this.context = context.getApplicationContext();
        data = new File(context.getFilesDir(), "study-data");
        data.mkdirs();
    }

    File dataDirectory() { return data; }
    File webDirectory() { return new File(context.getFilesDir(), "runtime"); }
    File manifestFile() { return new File(context.getFilesDir(), "resource-manifest.json"); }
    String progress() { return progress; }

    void prepareUi() throws Exception {
        copyTree("runtime", webDirectory());
        copyTree("tutorials", new File(context.getFilesDir(), "tutorials"));
        for (String artwork : new String[]{"splash.png", "icon.png"}) {
            try (InputStream source = context.getAssets().open("branding/"+artwork)) {
                copy(source, new File(context.getFilesDir(), "branding/"+artwork));
            }
        }
        try (InputStream source = context.getAssets().open("resource-manifest.json")) {
            copy(source, manifestFile());
        }
    }

    private void copyTree(String assetPath, File destination) throws Exception {
        String[] children = context.getAssets().list(assetPath);
        if (children != null && children.length > 0) {
            if (!destination.isDirectory() && !destination.mkdirs()) throw new IOException("Could not prepare app storage.");
            for (String name : children) copyTree(assetPath + "/" + name, new File(destination, name));
        } else {
            try (InputStream input = context.getAssets().open(assetPath)) { copy(input, destination); }
        }
    }

    private static void copy(InputStream source, File destination) throws IOException {
        File parent = destination.getParentFile();
        if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new IOException("Could not create storage folder.");
        try (FileOutputStream target = new FileOutputStream(destination)) {
            byte[] buffer = new byte[65536];
            int count;
            while ((count = source.read(buffer)) != -1) target.write(buffer, 0, count);
        }
    }

    JSONObject manifest() throws Exception {
        try (InputStream source = new FileInputStream(manifestFile())) {
            ByteArrayOutputStream bytes = new ByteArrayOutputStream();
            byte[] buffer = new byte[8192]; int count;
            while ((count = source.read(buffer)) != -1) bytes.write(buffer, 0, count);
            return new JSONObject(bytes.toString(StandardCharsets.UTF_8.name()));
        }
    }

    long requiredBytes() throws Exception {
        long remaining = 256L * 1024 * 1024;
        JSONArray files = manifest().getJSONArray("files");
        for (int i = 0; i < files.length(); i++) {
            JSONObject entry = files.getJSONObject(i);
            File file = safeDestination(entry.getString("path"));
            if (!file.isFile() || file.length() != entry.getLong("bytes")) remaining += entry.getLong("bytes");
        }
        return remaining;
    }

    private File safeDestination(String path) throws IOException {
        File destination = new File(data, path).getCanonicalFile();
        if (!destination.getPath().startsWith(data.getCanonicalPath() + File.separator)) throw new IOException("Invalid bundled resource location.");
        return destination;
    }

    private static String hex(byte[] bytes) {
        StringBuilder value = new StringBuilder();
        for (byte item : bytes) value.append(String.format(java.util.Locale.ROOT, "%02x", item & 255));
        return value.toString();
    }

    private static String hash(File file) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        try (InputStream input = new FileInputStream(file)) {
            byte[] buffer = new byte[1024 * 1024]; int count;
            while ((count = input.read(buffer)) != -1) digest.update(buffer, 0, count);
        }
        return hex(digest.digest());
    }

    private void report(long complete, long total, String message) throws Exception {
        JSONObject state = new JSONObject();
        state.put("completed", complete); state.put("total", total); state.put("message", message);
        progress = state.toString();
    }

    synchronized void install() throws Exception {
        JSONObject manifest = manifest();
        JSONArray entries = manifest.getJSONArray("files");
        long total = manifest.getLong("resource_bytes"), complete = 0;
        if (data.getUsableSpace() < requiredBytes()) throw new IOException("Not enough free storage. Free some space and retry setup.");
        for (int i = 0; i < entries.length(); i++) {
            JSONObject entry = entries.getJSONObject(i);
            String path = entry.getString("path");
            File destination = safeDestination(path);
            long expected = entry.getLong("bytes");
            if (destination.isFile()) {
                report(complete, total, "Checking prepared study resources…");
                if (destination.length() == expected && hash(destination).equals(entry.getString("sha256"))) {
                    complete += expected; continue;
                }
                // Never overwrite an existing writable reader database during a
                // retry: it may contain this person's marks and reading history.
                throw new IOException("An existing library needs recovery before setup. Your saved data was kept.");
            }
            File parent = destination.getParentFile();
            if (parent != null && !parent.isDirectory() && !parent.mkdirs()) throw new IOException("Could not create library storage.");
            File staging = safeDestination(path + ".installing");
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            long written = 0;
            try (InputStream input = context.getAssets().open(path, AssetManager.ACCESS_STREAMING);
                 FileOutputStream output = new FileOutputStream(staging)) {
                byte[] buffer = new byte[1024 * 1024]; int count;
                while ((count = input.read(buffer)) != -1) {
                    output.write(buffer, 0, count); digest.update(buffer, 0, count); written += count;
                    report(complete + written, total, "Preparing offline study resources…");
                }
                output.getFD().sync();
            }
            if (written != expected || !hex(digest.digest()).equals(entry.getString("sha256"))) {
                staging.delete(); throw new IOException("A bundled resource could not be verified. Retry setup.");
            }
            if (!staging.renameTo(destination)) throw new IOException("Could not finish preparing a library file.");
            complete += written;
        }
        report(total, total, "Your offline study library is ready.");
    }
}
