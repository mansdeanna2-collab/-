package com.videoapp.player

import android.os.Build
import android.util.Log
import androidx.multidex.MultiDexApplication
import coil.ImageLoader
import coil.ImageLoaderFactory
import coil.disk.DiskCache
import coil.memory.MemoryCache
import coil.request.CachePolicy
import coil.util.DebugLogger
import java.io.File

/**
 * Application class for Video Player app
 * Extends MultiDexApplication for better compatibility with older Android versions
 */
class VideoApp : MultiDexApplication(), ImageLoaderFactory {
    
    companion object {
        private const val TAG = "VideoApp"
        
        @Volatile
        private var _instance: VideoApp? = null
        
        val instance: VideoApp
            get() = _instance ?: throw IllegalStateException("VideoApp not initialized")
    }
    
    override fun onCreate() {
        super.onCreate()
        _instance = this
        
        // Setup global exception handler to prevent crashes
        setupGlobalExceptionHandler()
    }
    
    /**
     * Setup global uncaught exception handler for better crash resilience
     */
    private fun setupGlobalExceptionHandler() {
        val defaultHandler = Thread.getDefaultUncaughtExceptionHandler()
        
        Thread.setDefaultUncaughtExceptionHandler { thread, throwable ->
            try {
                // Log the exception
                Log.e(TAG, "Uncaught exception in thread ${thread.name}", throwable)
                Log.e(TAG, "Device: ${Build.MANUFACTURER} ${Build.MODEL}, Android ${Build.VERSION.RELEASE} (API ${Build.VERSION.SDK_INT})")
                
                // Log exception details for debugging
                val stackTrace = throwable.stackTrace.take(10).joinToString("\n") { 
                    "  at ${it.className}.${it.methodName}(${it.fileName}:${it.lineNumber})"
                }
                Log.e(TAG, "Stack trace:\n$stackTrace")
            } catch (e: Exception) {
                // Ignore any logging failures
            }
            
            // Call the default handler to terminate the app properly
            defaultHandler?.uncaughtException(thread, throwable)
        }
    }
    
    override fun newImageLoader(): ImageLoader {
        return try {
            val cacheDir = getCacheDirectory()
            
            ImageLoader.Builder(this)
                .memoryCache {
                    MemoryCache.Builder(this)
                        .maxSizePercent(0.20) // Use 20% of app memory for images (reduced for older devices)
                        .build()
                }
                .diskCache {
                    DiskCache.Builder()
                        .directory(cacheDir)
                        .maxSizePercent(0.02) // Use 2% of disk space
                        .build()
                }
                .memoryCachePolicy(CachePolicy.ENABLED)
                .diskCachePolicy(CachePolicy.ENABLED)
                .crossfade(true)
                .apply {
                    if (BuildConfig.DEBUG) {
                        logger(DebugLogger())
                    }
                }
                .build()
        } catch (e: Exception) {
            // Fallback to basic image loader if configuration fails
            Log.e(TAG, "Failed to create custom ImageLoader", e)
            createFallbackImageLoader()
        }
    }
    
    /**
     * Get or create cache directory safely
     */
    private fun getCacheDirectory(): File {
        return try {
            val dir = cacheDir.resolve("image_cache")
            if (!dir.exists()) {
                dir.mkdirs()
            }
            dir
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create cache directory", e)
            cacheDir
        }
    }
    
    /**
     * Create a simple fallback image loader
     */
    private fun createFallbackImageLoader(): ImageLoader {
        return try {
            ImageLoader.Builder(this)
                .crossfade(true)
                .build()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to create fallback ImageLoader", e)
            // Ultimate fallback - minimal configuration
            ImageLoader(this)
        }
    }
}
