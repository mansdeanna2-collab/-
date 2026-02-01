package com.videoapp.player;

import android.os.Build;
import android.util.Log;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.multidex.MultiDexApplication;

import coil.ImageLoader;
import coil.ImageLoaderFactory;
import coil.disk.DiskCache;
import coil.memory.MemoryCache;
import coil.request.CachePolicy;
import coil.util.DebugLogger;

import java.io.File;

/**
 * Application class for Video Player app
 * Extends MultiDexApplication for better compatibility with older Android versions
 *
 * Note: The singleton instance is set in onCreate() which is always called on the main thread
 * by the Android system before any other components are created.
 */
public class VideoApp extends MultiDexApplication implements ImageLoaderFactory {

    private static final String TAG = "VideoApp";

    // Volatile ensures visibility across threads. Thread-safety is guaranteed by the
    // Android framework which calls onCreate() on the main thread before any other
    // application code can execute.
    private static volatile VideoApp instance = null;

    @NonNull
    public static VideoApp getInstance() {
        VideoApp app = instance;
        if (app == null) {
            throw new IllegalStateException(
                    "VideoApp not initialized. This usually means the Application class " +
                            "was not properly configured in AndroidManifest.xml"
            );
        }
        return app;
    }

    /**
     * Safe accessor that returns null if not initialized
     * Use this in non-critical paths where the app can recover
     */
    @Nullable
    public static VideoApp getInstanceOrNull() {
        return instance;
    }

    @Override
    public void onCreate() {
        // Set instance first thing to prevent race conditions
        instance = this;

        try {
            super.onCreate();

            // Setup global exception handler to prevent crashes
            setupGlobalExceptionHandler();

            Log.i(TAG, "VideoApp initialized successfully");
            Log.i(TAG, "Device: " + Build.MANUFACTURER + " " + Build.MODEL +
                    ", Android " + Build.VERSION.RELEASE + " (API " + Build.VERSION.SDK_INT + ")");
        } catch (Exception e) {
            Log.e(TAG, "Error during VideoApp initialization", e);
            // Don't rethrow - let the app attempt to continue
        }
    }

    /**
     * Setup global uncaught exception handler for better crash resilience
     */
    private void setupGlobalExceptionHandler() {
        final Thread.UncaughtExceptionHandler defaultHandler = Thread.getDefaultUncaughtExceptionHandler();

        Thread.setDefaultUncaughtExceptionHandler(new Thread.UncaughtExceptionHandler() {
            @Override
            public void uncaughtException(@NonNull Thread thread, @NonNull Throwable throwable) {
                try {
                    // Log the exception
                    Log.e(TAG, "Uncaught exception in thread " + thread.getName(), throwable);
                    Log.e(TAG, "Device: " + Build.MANUFACTURER + " " + Build.MODEL +
                            ", Android " + Build.VERSION.RELEASE + " (API " + Build.VERSION.SDK_INT + ")");

                    // Log exception details for debugging
                    StackTraceElement[] stackTrace = throwable.getStackTrace();
                    StringBuilder sb = new StringBuilder();
                    int count = Math.min(10, stackTrace.length);
                    for (int i = 0; i < count; i++) {
                        StackTraceElement element = stackTrace[i];
                        sb.append("  at ").append(element.getClassName())
                                .append(".").append(element.getMethodName())
                                .append("(").append(element.getFileName())
                                .append(":").append(element.getLineNumber()).append(")\n");
                    }
                    Log.e(TAG, "Stack trace:\n" + sb.toString());

                    // Log cause if present
                    Throwable cause = throwable.getCause();
                    if (cause != null) {
                        Log.e(TAG, "Caused by: " + cause.getClass().getName() + ": " + cause.getMessage());
                    }
                } catch (Exception e) {
                    // Ignore any logging failures - we must not crash the crash handler
                }

                // Call the default handler to terminate the app properly
                if (defaultHandler != null) {
                    defaultHandler.uncaughtException(thread, throwable);
                }
            }
        });
    }

    @NonNull
    @Override
    public ImageLoader newImageLoader() {
        try {
            File cacheDir = getCacheDirectory();

            ImageLoader.Builder builder = new ImageLoader.Builder(this)
                    .memoryCache(new MemoryCache.Builder(this)
                            .maxSizePercent(0.20) // Use 20% of app memory for images (reduced for older devices)
                            .build())
                    .diskCache(new DiskCache.Builder()
                            .directory(cacheDir)
                            .maxSizePercent(0.02) // Use 2% of disk space
                            .build())
                    .memoryCachePolicy(CachePolicy.ENABLED)
                    .diskCachePolicy(CachePolicy.ENABLED)
                    .crossfade(true);

            if (BuildConfig.DEBUG) {
                builder.logger(new DebugLogger());
            }

            return builder.build();
        } catch (Exception e) {
            // Fallback to basic image loader if configuration fails
            Log.e(TAG, "Failed to create custom ImageLoader", e);
            return createFallbackImageLoader();
        }
    }

    /**
     * Get or create cache directory safely
     */
    @NonNull
    private File getCacheDirectory() {
        try {
            File dir = new File(getCacheDir(), "image_cache");
            if (!dir.exists()) {
                dir.mkdirs();
            }
            return dir;
        } catch (Exception e) {
            Log.e(TAG, "Failed to create cache directory", e);
            return getCacheDir();
        }
    }

    /**
     * Create a simple fallback image loader
     */
    @NonNull
    private ImageLoader createFallbackImageLoader() {
        try {
            return new ImageLoader.Builder(this)
                    .crossfade(true)
                    .build();
        } catch (Exception e) {
            Log.e(TAG, "Failed to create fallback ImageLoader", e);
            // Ultimate fallback - minimal configuration
            return new ImageLoader.Builder(this).build();
        }
    }
}
