package com.videoapp.player.util

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.util.Log

/**
 * Network utilities for checking connectivity
 */
object NetworkUtils {
    
    private const val TAG = "NetworkUtils"
    
    /**
     * Check if the device has an active network connection
     * Handles different API levels properly for Android 9+ compatibility
     */
    fun isNetworkAvailable(context: Context): Boolean {
        return try {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
                ?: return false
            
            val network = connectivityManager.activeNetwork
            if (network == null) {
                // Fallback for older behavior
                return isNetworkAvailableFallback(connectivityManager)
            }
            
            val capabilities = connectivityManager.getNetworkCapabilities(network)
            if (capabilities == null) {
                // Fallback if capabilities are null
                return isNetworkAvailableFallback(connectivityManager)
            }
            
            // Check for internet capability
            // Note: NET_CAPABILITY_VALIDATED might not be set on some networks,
            // so we also check for basic connectivity
            val hasInternet = capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
            val isValidated = capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
            
            // On Android 9 (API 28), some networks might not have VALIDATED flag set properly
            // So we accept if at least INTERNET capability is present
            if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
                // For Android 9 and below, be more lenient
                return hasInternet && (isValidated || 
                    capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI) ||
                    capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR))
            }
            
            hasInternet && isValidated
        } catch (e: Exception) {
            Log.e(TAG, "Error checking network availability", e)
            // In case of error, assume network is available to avoid blocking the user
            true
        }
    }
    
    /**
     * Fallback network check using deprecated API for maximum compatibility
     */
    @Suppress("DEPRECATION")
    private fun isNetworkAvailableFallback(connectivityManager: ConnectivityManager): Boolean {
        return try {
            val activeNetworkInfo = connectivityManager.activeNetworkInfo
            activeNetworkInfo?.isConnected == true
        } catch (e: Exception) {
            Log.e(TAG, "Error in fallback network check", e)
            true // Assume connected if we can't check
        }
    }
    
    /**
     * Check if connected to WiFi
     */
    fun isWifiConnected(context: Context): Boolean {
        return try {
            val connectivityManager = context.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager
                ?: return false
            
            val network = connectivityManager.activeNetwork ?: return false
            val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
            
            capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
        } catch (e: Exception) {
            Log.e(TAG, "Error checking WiFi connection", e)
            false
        }
    }
    
    /**
     * Get friendly network error message
     */
    fun getNetworkErrorMessage(context: Context): String {
        return if (!isNetworkAvailable(context)) {
            "网络连接不可用，请检查网络设置"
        } else {
            "网络请求失败，请稍后重试"
        }
    }
}
