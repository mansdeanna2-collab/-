# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in ${sdk.dir}/tools/proguard/proguard-android.txt

# Retrofit and Gson
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes EnclosingMethod
-keepattributes InnerClasses

# Retrofit
-dontwarn retrofit2.**
-keep class retrofit2.** { *; }
-keepclasseswithmembers class * {
    @retrofit2.http.* <methods>;
}

# Gson
-keep class com.videoapp.player.data.model.** { *; }
-keep class * implements com.google.gson.TypeAdapterFactory
-keep class * implements com.google.gson.JsonSerializer
-keep class * implements com.google.gson.JsonDeserializer

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep class okio.** { *; }

# Coroutines
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}

# Keep data classes
-keep class com.videoapp.player.data.model.Video { *; }
-keep class com.videoapp.player.data.model.Category { *; }
-keep class com.videoapp.player.data.model.VideoResponse { *; }
-keep class com.videoapp.player.data.model.SingleVideoResponse { *; }
-keep class com.videoapp.player.data.model.CategoryResponse { *; }
-keep class com.videoapp.player.data.model.Statistics { *; }
-keep class com.videoapp.player.data.model.StatisticsResponse { *; }

# Coil
-dontwarn coil.**
-keep class coil.** { *; }

# ExoPlayer / Media3
-dontwarn androidx.media3.**
-keep class androidx.media3.** { *; }
-keep interface androidx.media3.** { *; }
