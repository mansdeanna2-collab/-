package com.videoapp.player.data.api;

import com.videoapp.player.BuildConfig;

import okhttp3.OkHttpClient;
import okhttp3.logging.HttpLoggingInterceptor;
import retrofit2.Retrofit;
import retrofit2.converter.gson.GsonConverterFactory;

import java.util.concurrent.TimeUnit;

/**
 * Retrofit API client singleton
 */
public final class ApiClient {

    private static final long TIMEOUT_SECONDS = 30L;
    private static final String DEFAULT_BASE_URL = "http://103.74.193.179:5000/";

    private static ApiClient instance;
    private final Retrofit retrofit;
    private final VideoApiService videoApiService;

    private ApiClient() {
        HttpLoggingInterceptor loggingInterceptor = new HttpLoggingInterceptor();
        loggingInterceptor.setLevel(BuildConfig.DEBUG ?
                HttpLoggingInterceptor.Level.BODY :
                HttpLoggingInterceptor.Level.NONE);

        OkHttpClient okHttpClient = new OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .connectTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .readTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .writeTimeout(TIMEOUT_SECONDS, TimeUnit.SECONDS)
                .build();

        retrofit = new Retrofit.Builder()
                .baseUrl(getBaseUrl())
                .client(okHttpClient)
                .addConverterFactory(GsonConverterFactory.create())
                .build();

        videoApiService = retrofit.create(VideoApiService.class);
    }

    /**
     * Get the validated base URL for API calls
     */
    private String getBaseUrl() {
        String configuredUrl = BuildConfig.API_BASE_URL;

        // Check for placeholder or empty values
        if (configuredUrl == null || configuredUrl.trim().isEmpty() ||
                configuredUrl.equals("API_BASE_URL_PLACEHOLDER")) {
            return DEFAULT_BASE_URL;
        }

        // Ensure URL ends with /
        if (configuredUrl.endsWith("/")) {
            return configuredUrl;
        } else {
            return configuredUrl + "/";
        }
    }

    public static synchronized ApiClient getInstance() {
        if (instance == null) {
            instance = new ApiClient();
        }
        return instance;
    }

    public VideoApiService getVideoApiService() {
        return videoApiService;
    }
}
