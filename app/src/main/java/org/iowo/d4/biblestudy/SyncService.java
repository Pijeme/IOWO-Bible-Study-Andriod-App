package org.iowo.d4.biblestudy;

import android.app.*;
import android.content.Intent;
import android.os.*;
import com.chaquo.python.Python;
import org.json.JSONObject;
import java.util.concurrent.*;

/** Keeps an explicitly started backup visible while Android backgrounds the UI. */
public final class SyncService extends Service {
    private static final String CHANNEL = "study-backup";
    private ScheduledExecutorService poller;
    private long started;
    private int failures;
    @Override public void onCreate() {
        super.onCreate();
        ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).createNotificationChannel(
            new NotificationChannel(CHANNEL, "Bible Study backup", NotificationManager.IMPORTANCE_LOW));
    }
    private Notification notification(String message) {
        Intent open = new Intent(this, MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
        PendingIntent pending = PendingIntent.getActivity(this, 0, open, PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        return new Notification.Builder(this, CHANNEL).setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(getString(R.string.app_name)).setContentText(message).setOngoing(true)
            .setContentIntent(pending).build();
    }
    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        startForeground(41, notification(intent != null ? intent.getStringExtra("message") : "Checking backup progress"));
        if (poller == null) {
            started = System.currentTimeMillis();
            poller = Executors.newSingleThreadScheduledExecutor();
            poller.scheduleWithFixedDelay(() -> {
                try {
                    if (!Python.isStarted()) { stopSelf(); return; }
                    JSONObject job = new JSONObject(Python.getInstance().getModule("offline_app").callAttr("sync_status").toString());
                    failures = 0;
                    if (!job.optBoolean("running") && System.currentTimeMillis() - started > 5000) { stopSelf(); return; }
                    ((NotificationManager) getSystemService(NOTIFICATION_SERVICE)).notify(41,
                        notification(job.optString("message", "Backing up sermon notes")));
                } catch (Exception error) {
                    if (++failures >= 3) stopSelf();
                }
            }, 2, 3, TimeUnit.SECONDS);
        }
        // After a process kill the next in-app sync resumes saved request IDs;
        // this service does not manufacture a fresh upload behind the user's back.
        return START_NOT_STICKY;
    }
    @Override public void onDestroy() {
        if (poller != null) poller.shutdownNow();
        stopForeground(true); super.onDestroy();
    }
    @Override public IBinder onBind(Intent intent) { return null; }
}
