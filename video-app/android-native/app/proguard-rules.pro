# Add project specific ProGuard rules here.
# By default, the flags in this file are appended to flags specified
# in ${sdk.dir}/tools/proguard/proguard-android.txt

# General optimization settings
-optimizationpasses 5
-dontusemixedcaseclassnames
-verbose

# Keep source file names and line numbers for better crash reports
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile

# Retrofit and Gson
-keepattributes Signature
-keepattributes *Annotation*
-keepattributes EnclosingMethod
-keepattributes InnerClasses
-keepattributes Exceptions

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
-keepclassmembers,allowobfuscation class * {
    @com.google.gson.annotations.SerializedName <fields>;
}

# OkHttp
-dontwarn okhttp3.**
-dontwarn okio.**
-keep class okhttp3.** { *; }
-keep class okio.** { *; }

# Coroutines
-keepclassmembernames class kotlinx.** {
    volatile <fields>;
}
-keepnames class kotlinx.coroutines.internal.MainDispatcherFactory {}
-keepnames class kotlinx.coroutines.CoroutineExceptionHandler {}
-keepclassmembers class kotlinx.coroutines.** {
    volatile <fields>;
}
-dontwarn kotlinx.coroutines.**

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

# ViewModel and LiveData
-keep class * extends androidx.lifecycle.ViewModel { *; }
-keep class * extends androidx.lifecycle.AndroidViewModel { *; }

# PlayerViewModel Episode inner class
-keep class com.videoapp.player.ui.player.PlayerViewModel$Episode { *; }

# Keep Application class
-keep class com.videoapp.player.VideoApp { *; }

# Keep Activities
-keep class com.videoapp.player.ui.home.HomeActivity { *; }
-keep class com.videoapp.player.ui.player.PlayerActivity { *; }

# Keep ViewModels
-keep class com.videoapp.player.ui.home.HomeViewModel { *; }
-keep class com.videoapp.player.ui.player.PlayerViewModel { *; }

# Keep adapters
-keep class com.videoapp.player.ui.adapter.** { *; }

# Keep API service
-keep class com.videoapp.player.data.api.** { *; }

# Keep repositories
-keep class com.videoapp.player.data.repository.** { *; }

# Keep utility classes
-keep class com.videoapp.player.util.** { *; }

# Multidex
-keep class androidx.multidex.** { *; }

# AndroidX
-dontwarn androidx.**
-keep class androidx.** { *; }
-keep interface androidx.** { *; }

# Keep Kotlin metadata
-keepattributes RuntimeVisibleAnnotations
-keep class kotlin.Metadata { *; }

# Prevent stripping of methods with parameters annotated with @Nullable or @NonNull
-keepattributes RuntimeVisibleParameterAnnotations
