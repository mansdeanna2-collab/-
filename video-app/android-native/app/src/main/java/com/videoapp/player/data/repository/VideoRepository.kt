package com.videoapp.player.data.repository

import android.util.Log
import com.videoapp.player.data.api.ApiClient
import com.videoapp.player.data.model.*
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/**
 * Video repository for managing video data
 */
class VideoRepository {
    
    companion object {
        private const val TAG = "VideoRepository"
    }
    
    private val apiService = ApiClient.videoApiService
    
    /**
     * Convert exception to user-friendly message
     */
    private fun getErrorMessage(e: Exception): String {
        return when (e) {
            is CancellationException -> throw e // Re-throw cancellation exceptions
            is UnknownHostException -> "无法连接到服务器，请检查网络"
            is SocketTimeoutException -> "连接超时，请稍后重试"
            is ConnectException -> "连接被拒绝，请稍后重试"
            else -> {
                Log.e(TAG, "API error: ${e.message}", e)
                e.message ?: "请求失败"
            }
        }
    }
    
    /**
     * Get videos with pagination
     */
    suspend fun getVideos(limit: Int = 20, offset: Int = 0): Result<List<Video>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getVideos(limit, offset)
                if (response.isSuccessful) {
                    val videos = response.body()?.data ?: emptyList()
                    Result.success(videos)
                } else {
                    Log.w(TAG, "getVideos failed with code: ${response.code()}")
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Result.failure(Exception(getErrorMessage(e)))
            }
        }
    }
    
    /**
     * Get a single video by ID
     */
    suspend fun getVideo(videoId: Int): Result<Video> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getVideo(videoId)
                if (response.isSuccessful) {
                    response.body()?.data?.let {
                        Result.success(it)
                    } ?: Result.failure(Exception("视频不存在"))
                } else {
                    Log.w(TAG, "getVideo failed with code: ${response.code()}")
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Result.failure(Exception(getErrorMessage(e)))
            }
        }
    }
    
    /**
     * Search videos by keyword
     */
    suspend fun searchVideos(keyword: String, limit: Int = 20, offset: Int = 0): Result<List<Video>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.searchVideos(keyword, limit, offset)
                if (response.isSuccessful) {
                    val videos = response.body()?.data ?: emptyList()
                    Result.success(videos)
                } else {
                    Log.w(TAG, "searchVideos failed with code: ${response.code()}")
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Result.failure(Exception(getErrorMessage(e)))
            }
        }
    }
    
    /**
     * Get videos by category
     */
    suspend fun getVideosByCategory(category: String, limit: Int = 20, offset: Int = 0): Result<List<Video>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getVideosByCategory(category, limit, offset)
                if (response.isSuccessful) {
                    val videos = response.body()?.data ?: emptyList()
                    Result.success(videos)
                } else {
                    Log.w(TAG, "getVideosByCategory failed with code: ${response.code()}")
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Result.failure(Exception(getErrorMessage(e)))
            }
        }
    }
    
    /**
     * Get top videos
     */
    suspend fun getTopVideos(limit: Int = 10): Result<List<Video>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getTopVideos(limit)
                if (response.isSuccessful) {
                    val videos = response.body()?.data ?: emptyList()
                    Result.success(videos)
                } else {
                    Log.w(TAG, "getTopVideos failed with code: ${response.code()}")
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Result.failure(Exception(getErrorMessage(e)))
            }
        }
    }
    
    /**
     * Update play count for a video
     */
    suspend fun updatePlayCount(videoId: Int): Result<Unit> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.updatePlayCount(videoId)
                if (response.isSuccessful) {
                    Result.success(Unit)
                } else {
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                // Silently fail for play count updates
                Log.d(TAG, "updatePlayCount failed: ${e.message}")
                Result.failure(e)
            }
        }
    }
    
    /**
     * Get all categories
     */
    suspend fun getCategories(): Result<List<Category>> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getCategories()
                if (response.isSuccessful) {
                    val categories = response.body()?.data ?: emptyList()
                    Result.success(categories)
                } else {
                    Log.w(TAG, "getCategories failed with code: ${response.code()}")
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Result.failure(Exception(getErrorMessage(e)))
            }
        }
    }
    
    /**
     * Get statistics
     */
    suspend fun getStatistics(): Result<Statistics> {
        return withContext(Dispatchers.IO) {
            try {
                val response = apiService.getStatistics()
                if (response.isSuccessful) {
                    response.body()?.data?.let {
                        Result.success(it)
                    } ?: Result.failure(Exception("统计信息不可用"))
                } else {
                    Log.w(TAG, "getStatistics failed with code: ${response.code()}")
                    Result.failure(Exception("服务器错误: ${response.code()}"))
                }
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                Result.failure(Exception(getErrorMessage(e)))
            }
        }
    }
}
