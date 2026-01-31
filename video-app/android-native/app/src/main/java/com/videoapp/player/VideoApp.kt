package com.videoapp.player

import android.app.Application
import android.util.Log
import coil.ImageLoader
import coil.ImageLoaderFactory
import coil.disk.DiskCache
import coil.memory.MemoryCache
import coil.request.CachePolicy
import coil.util.DebugLogger

/**
 * Application class for Video Player app
 */
class VideoApp : Application(), ImageLoaderFactory {
    
    override fun onCreate() {
        super.onCreate()
        _instance = this
    }
    
    override fun newImageLoader(): ImageLoader {
        return try {
            ImageLoader.Builder(this)
                .memoryCache {
                    MemoryCache.Builder(this)
                        .maxSizePercent(0.25) // Use 25% of app memory for images
                        .build()
                }
                .diskCache {
                    DiskCache.Builder()
                        .directory(cacheDir.resolve("image_cache"))
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
            Log.e("VideoApp", "Failed to create custom ImageLoader", e)
            ImageLoader.Builder(this)
                .crossfade(true)
                .build()
        }
    }
    
    companion object {
        @Volatile
        private var _instance: VideoApp? = null
        
        val instance: VideoApp
            get() = _instance ?: throw IllegalStateException("VideoApp not initialized")
    }
}
