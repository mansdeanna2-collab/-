package com.videoapp.player.util;

import android.content.Context;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkInfo;
import android.util.Log;

import androidx.annotation.NonNull;

/**
 * Network utilities for checking connectivity
 */
public final class NetworkUtils {

    private static final String TAG = "NetworkUtils";

    private NetworkUtils() {
        // Private constructor to prevent instantiation
    }

    /**
     * Check if the device has an active network connection
     * Handles different API levels properly for Android 9+ compatibility
     */
    public static boolean isNetworkAvailable(@NonNull Context context) {
        try {
            ConnectivityManager connectivityManager =
                    (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            if (connectivityManager == null) {
                return false;
            }

            Network network = connectivityManager.getActiveNetwork();
            if (network == null) {
                // Fallback for older behavior
                return isNetworkAvailableFallback(connectivityManager);
            }

            NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(network);
            if (capabilities == null) {
                // Fallback if capabilities are null
                return isNetworkAvailableFallback(connectivityManager);
            }

            // Check for internet capability
            // Note: NET_CAPABILITY_VALIDATED might not be set on some networks,
            // so we also check for basic connectivity
            boolean hasInternet = capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET);
            boolean hasTransport = capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
                    || capabilities.hasTransport(NetworkCapabilities.TRANSPORT_CELLULAR)
                    || capabilities.hasTransport(NetworkCapabilities.TRANSPORT_ETHERNET);

            // Be lenient with network validation to avoid blocking legitimate connections
            // Some networks (especially on older devices or specific network configurations)
            // may not properly report the VALIDATED flag
            // If we have internet capability and a valid transport, allow connection
            // The actual API call will fail gracefully if there's no real connectivity
            return hasInternet && hasTransport;
        } catch (Exception e) {
            Log.e(TAG, "Error checking network availability", e);
            // In case of error, return false to be safe - let the calling code handle it
            return false;
        }
    }

    /**
     * Fallback network check using deprecated API for maximum compatibility
     */
    @SuppressWarnings("deprecation")
    private static boolean isNetworkAvailableFallback(@NonNull ConnectivityManager connectivityManager) {
        try {
            NetworkInfo activeNetworkInfo = connectivityManager.getActiveNetworkInfo();
            return activeNetworkInfo != null && activeNetworkInfo.isConnected();
        } catch (Exception e) {
            Log.e(TAG, "Error in fallback network check", e);
            return false; // Return false if we can't determine connectivity
        }
    }

    /**
     * Check if connected to WiFi
     */
    public static boolean isWifiConnected(@NonNull Context context) {
        try {
            ConnectivityManager connectivityManager =
                    (ConnectivityManager) context.getSystemService(Context.CONNECTIVITY_SERVICE);
            if (connectivityManager == null) {
                return false;
            }

            Network network = connectivityManager.getActiveNetwork();
            if (network == null) {
                return false;
            }

            NetworkCapabilities capabilities = connectivityManager.getNetworkCapabilities(network);
            if (capabilities == null) {
                return false;
            }

            return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI);
        } catch (Exception e) {
            Log.e(TAG, "Error checking WiFi connection", e);
            return false;
        }
    }

    /**
     * Get friendly network error message
     */
    @NonNull
    public static String getNetworkErrorMessage(@NonNull Context context) {
        if (!isNetworkAvailable(context)) {
            return "网络连接不可用，请检查网络设置";
        } else {
            return "网络请求失败，请稍后重试";
        }
    }
}
