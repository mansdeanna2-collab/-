package com.videoapp.player.data.api

import com.videoapp.player.BuildConfig
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Retrofit API client singleton
 */
object ApiClient {
    
    private const val TIMEOUT_SECONDS = 30L
    private const val DEFAULT_BASE_URL = "http://localhost:8000/"
    
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = if (BuildConfig.DEBUG) {
            HttpLoggingInterceptor.Level.BODY
        } else {
            HttpLoggingInterceptor.Level.NONE
        }
    }
    
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
        .build()
    
    /**
     * Get the validated base URL for API calls
     */
    private fun getBaseUrl(): String {
        val configuredUrl = BuildConfig.API_BASE_URL
        
        // Check for placeholder or empty values
        if (configuredUrl.isBlank() || configuredUrl == "API_BASE_URL_PLACEHOLDER") {
            return DEFAULT_BASE_URL
        }
        
        // Ensure URL ends with /
        return if (configuredUrl.endsWith("/")) {
            configuredUrl
        } else {
            "$configuredUrl/"
        }
    }
    
    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(getBaseUrl())
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    val videoApiService: VideoApiService by lazy {
        retrofit.create(VideoApiService::class.java)
    }
}
