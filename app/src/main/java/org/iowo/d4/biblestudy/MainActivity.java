package org.iowo.d4.biblestudy;

import android.Manifest;
import android.app.*;
import android.content.*;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.graphics.drawable.Drawable;
import android.net.Uri;
import android.os.*;
import android.view.*;
import android.webkit.*;
import android.widget.*;
import androidx.webkit.WebViewAssetLoader;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;
import org.json.JSONObject;
import org.json.JSONArray;
import java.io.*;

public final class MainActivity extends Activity {
    private static NativeServices services;
    private FrameLayout root;
    private WebView reader;
    private TextView loading;
    private String baseUrl;
    private String pendingUrl;
    private Dialog aboutDialog, tutorialDialog;
    private WebView tutorialView;
    private ProgressBar startupProgress;
    private TextView startupVerse;
    private JSONArray startupVerses;
    private int verseIndex;
    private boolean readerPrepared=false, startupFailed=false;
    private final Runnable rotateVerse=new Runnable() {
        @Override public void run() {
            if(readerPrepared || isFinishing()) return;
            showStartupVerse(); ui.postDelayed(this,5000);
        }
    };
    private final Handler ui = new Handler(Looper.getMainLooper());

    private int dp(int value) { return Math.round(getResources().getDisplayMetrics().density * value); }

    @Override public void onCreate(Bundle saved) {
        super.onCreate(saved);
        getWindow().setStatusBarColor(Color.rgb(20, 37, 78));
        getWindow().setNavigationBarColor(Color.rgb(20, 37, 78));
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.rgb(10, 31, 70));
        root.setOnApplyWindowInsetsListener((view, insets) -> {
            view.setPadding(insets.getSystemWindowInsetLeft(), insets.getSystemWindowInsetTop(),
                            insets.getSystemWindowInsetRight(), insets.getSystemWindowInsetBottom());
            return insets;
        });
        setContentView(root);
        if (services == null) services = new NativeServices(getApplicationContext());
        services.attach(this);
        showSplash();
        if(!getPreferences(MODE_PRIVATE).getBoolean("tutorial-intro-seen",false))
            ui.post(() -> showTutorials(true));
        reportStudyProgress(3,"Preparing your offline workspace");
        new Thread(() -> {
            try {
                services.installer.prepareUi();
                runOnUiThread(() -> reportStudyProgress(15,"Starting the Bible Study engine"));
                synchronized (Python.class) {
                    if (!Python.isStarted()) Python.start(new AndroidPlatform(getApplicationContext()));
                }
                JSONObject result = new JSONObject(Python.getInstance().getModule("offline_app").callAttr("start_android",
                    services, services.installer.dataDirectory().getAbsolutePath(),
                    services.installer.webDirectory().getAbsolutePath(), services.installer.manifestFile().getAbsolutePath()).toString());
                baseUrl = result.getString("url");
                String gate = result.getString("gate");
                runOnUiThread(() -> {
                    CookieManager cookies = CookieManager.getInstance(); cookies.setAcceptCookie(true);
                    cookies.setCookie(baseUrl, "iowo_device_gate=" + gate + "; Path=/; HttpOnly; SameSite=Strict", accepted -> {
                        cookies.flush();
                        reportStudyProgress(40,"Preparing your Bible and saved notes");
                        pendingUrl=baseUrl+"/"; openReader();
                    });
                });
            } catch (Exception error) {
                runOnUiThread(() -> showStartupError());
            }
        }, "offline-startup").start();
    }

    private void showSplash() {
        root.removeAllViews();
        ImageView artwork = new ImageView(this);
        artwork.setScaleType(ImageView.ScaleType.FIT_CENTER);
        artwork.setContentDescription("IOWO D4 Bible Study");
        try (InputStream image = getAssets().open("branding/splash.png")) {
            artwork.setImageDrawable(Drawable.createFromStream(image, "splash"));
        } catch (IOException ignored) { artwork.setImageResource(R.drawable.app_icon); }
        root.addView(artwork, new FrameLayout.LayoutParams(-1, -1));
        LinearLayout preparation=new LinearLayout(this);
        preparation.setOrientation(LinearLayout.VERTICAL); preparation.setPadding(dp(18),dp(14),dp(18),dp(14));
        GradientDrawable surface=new GradientDrawable(); surface.setColor(0xEE102449); surface.setCornerRadius(dp(16));
        preparation.setBackground(surface);
        loading=new TextView(this); loading.setText(R.string.loading); loading.setTextColor(Color.WHITE); loading.setTextSize(13);
        loading.setGravity(Gravity.CENTER); preparation.addView(loading);
        startupProgress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);
        startupProgress.setMax(100); startupProgress.setIndeterminate(false);
        startupProgress.setProgressTintList(android.content.res.ColorStateList.valueOf(Color.rgb(230,199,128)));
        LinearLayout.LayoutParams bar=new LinearLayout.LayoutParams(-1,dp(9)); bar.topMargin=dp(10); bar.bottomMargin=dp(12);
        preparation.addView(startupProgress,bar);
        startupVerse=new TextView(this); startupVerse.setTextColor(Color.rgb(255,247,223)); startupVerse.setTextSize(14);
        startupVerse.setGravity(Gravity.CENTER); startupVerse.setLineSpacing(dp(3),1); preparation.addView(startupVerse);
        Typeface interfaceFont=Typeface.create("sans-serif",Typeface.NORMAL);
        try { interfaceFont=Typeface.createFromAsset(getAssets(),"runtime/static/fonts/SpaceGrotesk-Variable.ttf"); }
        catch(RuntimeException ignored) { }
        loading.setTypeface(interfaceFont); startupVerse.setTypeface(interfaceFont);
        FrameLayout.LayoutParams status=new FrameLayout.LayoutParams(-1,-2,Gravity.BOTTOM);
        status.bottomMargin=dp(82); status.leftMargin=status.rightMargin=dp(20); root.addView(preparation,status);
        try(InputStream input=getAssets().open("branding/startup-verses.json")) {
            ByteArrayOutputStream bytes=new ByteArrayOutputStream(); byte[] buffer=new byte[4096]; int count;
            while((count=input.read(buffer))!=-1) bytes.write(buffer,0,count);
            startupVerses=new JSONArray(bytes.toString("UTF-8"));
            verseIndex=getPreferences(MODE_PRIVATE).getInt("startup-verse",0)%startupVerses.length();
            getPreferences(MODE_PRIVATE).edit().putInt("startup-verse",(verseIndex+1)%startupVerses.length()).apply();
        } catch(Exception ignored) { startupVerses=null; }
        ui.post(rotateVerse);
        Button about = new Button(this);
        about.setText(R.string.about_publisher); about.setTextColor(Color.rgb(23, 46, 78));
        about.setAllCaps(false); about.setTypeface(interfaceFont); about.setLetterSpacing(.02f);
        about.setPadding(dp(24),0,dp(24),0);
        GradientDrawable buttonSurface = new GradientDrawable();
        buttonSurface.setColor(0xF2FFFBF0); buttonSurface.setCornerRadius(dp(24));
        buttonSurface.setStroke(dp(1),Color.rgb(158,189,202)); about.setBackground(buttonSurface);
        FrameLayout.LayoutParams action = new FrameLayout.LayoutParams(-2, dp(50), Gravity.BOTTOM | Gravity.CENTER_HORIZONTAL);
        action.bottomMargin = dp(20);
        LinearLayout actions=new LinearLayout(this); actions.setGravity(Gravity.CENTER);
        about.setPadding(dp(16),0,dp(16),0);
        actions.addView(about,new LinearLayout.LayoutParams(-2,dp(50)));
        Button tutorials=new Button(this); tutorials.setText("Tutorials"); tutorials.setAllCaps(false);
        tutorials.setTextColor(Color.WHITE); tutorials.setTypeface(interfaceFont);
        GradientDrawable tutorialSurface=new GradientDrawable(); tutorialSurface.setColor(0xEE236C72);
        tutorialSurface.setCornerRadius(dp(24)); tutorials.setBackground(tutorialSurface);
        tutorials.setPadding(dp(22),0,dp(22),0);
        LinearLayout.LayoutParams tutorialAction=new LinearLayout.LayoutParams(-2,dp(50));tutorialAction.leftMargin=dp(10);
        actions.addView(tutorials,tutorialAction);root.addView(actions,action);
        about.setOnClickListener(view -> showAbout());tutorials.setOnClickListener(view -> showTutorials(false));
    }

    private void showStartupVerse() {
        try {
            if(startupVerses==null || startupVerses.length()==0) return;
            JSONObject verse=startupVerses.getJSONObject(verseIndex++%startupVerses.length());
            startupVerse.setText(verse.getString("text")+"\n\n"+verse.getString("reference")+" (NIV)");
        } catch(Exception ignored) { }
    }
    void reportStudyProgress(int value,String message) {
        if(readerPrepared || startupFailed || startupProgress==null) return;
        startupProgress.setProgress(Math.max(startupProgress.getProgress(),Math.min(100,value))); loading.setText(message);
    }
    void workspaceReady() {
        readerPrepared=true; ui.removeCallbacks(rotateVerse);
        revealReader();
    }
    private void revealReader() {
        if(isFinishing() || reader==null || !readerPrepared ||
            (aboutDialog!=null && aboutDialog.isShowing()) || (tutorialDialog!=null && tutorialDialog.isShowing())) return;
        root.removeAllViews(); reader.setAlpha(1f); reader.setEnabled(true);
        reader.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_AUTO);
        root.addView(reader,new FrameLayout.LayoutParams(-1,-1));
    }
    void startupPreparationFailed() { showStartupError(); }

    private void showStartupError() {
        if(startupFailed || isFinishing()) return;
        startupFailed=true; ui.removeCallbacks(rotateVerse); loading.setText(R.string.startup_error);
        new AlertDialog.Builder(this).setTitle("Could not open Bible Study")
            .setMessage("Please reopen the app. If setup was interrupted, it can resume without removing your notes.")
            .setPositiveButton("Retry",(dialog,which) -> recreate())
            .setNegativeButton("Close",(dialog,which) -> finish()).show();
    }

    private boolean local(Uri uri) {
        if (baseUrl == null) return false;
        Uri base = Uri.parse(baseUrl);
        return "http".equals(uri.getScheme()) && "127.0.0.1".equals(uri.getHost()) && uri.getPort() == base.getPort();
    }

    private void external(Uri uri) {
        String scheme = uri.getScheme();
        if (!("https".equals(scheme) || "http".equals(scheme) || "mailto".equals(scheme) || "tel".equals(scheme))) return;
        try { startActivity(new Intent(Intent.ACTION_VIEW, uri)); }
        catch (ActivityNotFoundException error) { Toast.makeText(this, "No app is available to open this link.", Toast.LENGTH_SHORT).show(); }
    }

    private void openReader() {
        if(isFinishing()) return;
        if(pendingUrl==null) { revealReader(); return; }
        if (reader == null) {
            reader = new WebView(this);
            WebSettings settings = reader.getSettings();
            settings.setJavaScriptEnabled(true); settings.setDomStorageEnabled(true);
            settings.setAllowFileAccess(false); settings.setAllowContentAccess(false);
            settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
            settings.setCacheMode(WebSettings.LOAD_NO_CACHE);
            settings.setBuiltInZoomControls(true); settings.setDisplayZoomControls(false);
            CookieManager.getInstance().setAcceptThirdPartyCookies(reader, false);
            reader.addJavascriptInterface(services, "IOWOAndroid");
            reader.setWebChromeClient(new WebChromeClient());
            reader.setWebViewClient(new WebViewClient() {
                @Override public void onPageFinished(WebView view,String url) {
                    if(!local(Uri.parse(url))) return;
                    view.evaluateJavascript("!!document.getElementById('bibleStudyRoot')",isReader -> {
                        if("false".equals(isReader)) workspaceReady();
                    });
                }

                @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                    if (local(request.getUrl())) return false;
                    if (request.hasGesture()) external(request.getUrl());
                    return true;
                }
                @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                    Uri uri = request.getUrl();
                    if (local(uri) || "data".equals(uri.getScheme()) || "blob".equals(uri.getScheme())) return null;
                    return new WebResourceResponse("text/plain", "UTF-8", 403, "Offline app resources only",
                        java.util.Collections.emptyMap(), new ByteArrayInputStream(new byte[0]));
                }
                @Override public void onReceivedSslError(WebView view, android.webkit.SslErrorHandler handler, android.net.http.SslError error) {
                    handler.cancel();
                }
            });
        }
        // Prepare the local reader behind the splash until JS reports readiness.
        reader.setAlpha(0f); reader.setEnabled(false);
        reader.setImportantForAccessibility(View.IMPORTANT_FOR_ACCESSIBILITY_NO_HIDE_DESCENDANTS);
        if(reader.getParent()==null) root.addView(reader,0,new FrameLayout.LayoutParams(-1,-1));
        reader.loadUrl(pendingUrl); pendingUrl=null;
        ui.postDelayed(() -> { if(!readerPrepared) showStartupError(); },120000);
    }

    private void showAbout() {
        if (aboutDialog != null && aboutDialog.isShowing()) return;
        Dialog dialog = new Dialog(this, android.R.style.Theme_Material_Light_NoActionBar);
        LinearLayout content = new LinearLayout(this); content.setOrientation(LinearLayout.VERTICAL);
        Button close = new Button(this); close.setText(R.string.back_to_app); content.addView(close, new LinearLayout.LayoutParams(-1, dp(48)));
        WebView about = new WebView(this); about.getSettings().setJavaScriptEnabled(true);
        about.getSettings().setAllowFileAccess(false); about.getSettings().setAllowContentAccess(false);
        WebViewAssetLoader assets = new WebViewAssetLoader.Builder()
            .addPathHandler("/assets/", new WebViewAssetLoader.AssetsPathHandler(this)).build();
        about.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view, WebResourceRequest request) {
                WebResourceResponse response = assets.shouldInterceptRequest(request.getUrl());
                return response != null ? response : new WebResourceResponse("text/plain", "UTF-8", new ByteArrayInputStream(new byte[0]));
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view, WebResourceRequest request) {
                if ("appassets.androidplatform.net".equals(request.getUrl().getHost())) return false;
                if (request.hasGesture()) external(request.getUrl());
                return true;
            }
        });
        content.addView(about, new LinearLayout.LayoutParams(-1, 0, 1));
        dialog.setContentView(content); aboutDialog = dialog;
        close.setOnClickListener(view -> dialog.dismiss());
        dialog.setOnDismissListener(ignored -> { about.destroy(); aboutDialog = null; if (pendingUrl != null) openReader(); else revealReader(); });
        dialog.show();
        if (dialog.getWindow() != null) dialog.getWindow().setLayout(-1, -1);
        about.loadUrl("https://appassets.androidplatform.net/assets/about-developer/index.html");
    }

    // The guide is bundled independently of Python, login and library setup.
    // Its bridge exposes only closing the guide, never account APIs.
    void showTutorials(boolean firstUse) {
        if(isFinishing() || (tutorialDialog!=null && tutorialDialog.isShowing())) return;
        services.tutorialVisible=true;
        Dialog dialog=new Dialog(this,android.R.style.Theme_Material_Light_NoActionBar);
        WebView guide=new WebView(this); tutorialView=guide; tutorialDialog=dialog;
        WebSettings settings=guide.getSettings();settings.setJavaScriptEnabled(true);settings.setDomStorageEnabled(true);
        settings.setAllowFileAccess(false);settings.setAllowContentAccess(false);
        settings.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);
        guide.setWebChromeClient(new WebChromeClient());
        guide.addJavascriptInterface(new Object() {
            @JavascriptInterface public void finish() { runOnUiThread(dialog::dismiss); }
        },"IOWOTutorial");
        WebViewAssetLoader assets=new WebViewAssetLoader.Builder()
            .addPathHandler("/assets/",new WebViewAssetLoader.AssetsPathHandler(this)).build();
        guide.setWebViewClient(new WebViewClient() {
            @Override public WebResourceResponse shouldInterceptRequest(WebView view,WebResourceRequest request) {
                Uri uri=request.getUrl();String path=uri.getPath();
                if("https".equals(uri.getScheme()) && "appassets.androidplatform.net".equals(uri.getHost()) && path!=null &&
                    (path.startsWith("/assets/tutorials/") || path.startsWith("/assets/runtime/static/fonts/"))) {
                    WebResourceResponse response=assets.shouldInterceptRequest(uri);if(response!=null)return response;
                }
                return new WebResourceResponse("text/plain","UTF-8",new ByteArrayInputStream(new byte[0]));
            }
            @Override public boolean shouldOverrideUrlLoading(WebView view,WebResourceRequest request) {
                Uri uri=request.getUrl();return !("https".equals(uri.getScheme()) &&
                    "appassets.androidplatform.net".equals(uri.getHost()) && "/assets/tutorials/index.html".equals(uri.getPath()));
            }
        });
        dialog.setContentView(guide);
        dialog.setOnKeyListener((source,key,event) -> {
            if(key!=KeyEvent.KEYCODE_BACK)return false;
            if(event.getAction()==KeyEvent.ACTION_UP) guide.evaluateJavascript(
                "window.iowoTutorialBack ? window.iowoTutorialBack() : false",handled -> {
                    if(!"true".equals(handled))dialog.dismiss();
                });
            return true;
        });
        dialog.setOnDismissListener(ignored -> {
            if(firstUse)getPreferences(MODE_PRIVATE).edit().putBoolean("tutorial-intro-seen",true).apply();
            services.tutorialVisible=false;tutorialDialog=null;tutorialView=null;
            guide.removeJavascriptInterface("IOWOTutorial");guide.destroy();
            if(pendingUrl!=null)openReader();else revealReader();
            if(reader!=null)reader.evaluateJavascript("window.dispatchEvent(new Event('iowo-tutorial-closed'))",null);
        });
        dialog.show();if(dialog.getWindow()!=null)dialog.getWindow().setLayout(-1,-1);
        guide.loadUrl("https://appassets.androidplatform.net/assets/tutorials/index.html"+(firstUse?"?tour=1":""));
    }

    void offerNotificationPermission() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED &&
            !getPreferences(MODE_PRIVATE).getBoolean("notifications-asked", false)) {
            getPreferences(MODE_PRIVATE).edit().putBoolean("notifications-asked", true).apply();
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS}, 7002);
        }
    }

    @Override public void onBackPressed() {
        if (aboutDialog != null && aboutDialog.isShowing()) { aboutDialog.dismiss(); return; }
        if (reader == null) { super.onBackPressed(); return; }
        reader.evaluateJavascript("window.iowoHandleBack ? window.iowoHandleBack() : false", handled -> {
            if ("true".equals(handled)) return;
            if (reader.canGoBack()) reader.goBack(); else MainActivity.super.onBackPressed();
        });
    }
    @Override protected void onActivityResult(int request, int result, Intent data) {
        super.onActivityResult(request, result, data);
        if (request == NativeServices.SAVE_DOCUMENT) services.saveDocumentResult(result, data == null ? null : data.getData());
    }
    @Override protected void onPause() { if (reader != null) reader.onPause(); super.onPause(); }
    @Override protected void onResume() { super.onResume(); if (reader != null) reader.onResume(); }
    @Override protected void onDestroy() { ui.removeCallbacksAndMessages(null);
        if(tutorialDialog!=null){tutorialDialog.setOnDismissListener(null);tutorialDialog.dismiss();tutorialDialog=null;}
        if(tutorialView!=null){tutorialView.removeJavascriptInterface("IOWOTutorial");tutorialView.destroy();tutorialView=null;}
        services.tutorialVisible=false; if (reader != null) { reader.removeJavascriptInterface("IOWOAndroid"); reader.destroy(); } super.onDestroy(); }
}
