package com.videoapp.player.ui.player

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.videoapp.player.data.model.Video
import com.videoapp.player.data.repository.VideoRepository
import kotlinx.coroutines.launch

/**
 * ViewModel for PlayerActivity
 */
class PlayerViewModel : ViewModel() {
    
    private val repository = VideoRepository()
    
    // Current video
    private val _video = MutableLiveData<Video?>()
    val video: LiveData<Video?> = _video
    
    // Related videos
    private val _relatedVideos = MutableLiveData<List<Video>>(emptyList())
    val relatedVideos: LiveData<List<Video>> = _relatedVideos
    
    // Loading state
    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading
    
    // Error state
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    // Current video ID
    private var currentVideoId: Int = 0
    
    /**
     * Load video by ID
     */
    fun loadVideo(videoId: Int) {
        if (videoId == currentVideoId && _video.value != null) return
        
        currentVideoId = videoId
        
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            val result = repository.getVideo(videoId)
            
            result.fold(
                onSuccess = { video ->
                    _video.value = video
                    // Load related videos
                    loadRelatedVideos(video)
                },
                onFailure = { e ->
                    _error.value = e.message ?: "加载视频失败"
                }
            )
            
            _isLoading.value = false
        }
    }
    
    /**
     * Load related videos based on category
     */
    private suspend fun loadRelatedVideos(video: Video) {
        if (video.videoCategory.isNullOrEmpty()) {
            _relatedVideos.value = emptyList()
            return
        }
        
        val result = repository.getVideosByCategory(video.videoCategory, 6, 0)
        
        result.fold(
            onSuccess = { videos ->
                // Filter out current video
                _relatedVideos.value = videos.filter { it.videoId != video.videoId }
            },
            onFailure = {
                _relatedVideos.value = emptyList()
            }
        )
    }
    
    /**
     * Update play count when video starts playing
     */
    fun updatePlayCount(videoId: Int) {
        viewModelScope.launch {
            repository.updatePlayCount(videoId)
        }
    }
    
    /**
     * Clear error message
     */
    fun clearError() {
        _error.value = null
    }
    
    /**
     * Get parsed video URLs for multi-episode content
     * Format: name1$url1#name2$url2
     */
    fun getEpisodes(): List<Episode> {
        val video = _video.value ?: return emptyList()
        val url = video.videoUrl
        
        if (url.isBlank()) return emptyList()
        
        return try {
            if (url.contains("#")) {
                url.split("#").mapIndexedNotNull { index, part ->
                    if (part.isBlank()) return@mapIndexedNotNull null
                    if (part.contains("$")) {
                        val parts = part.split("$", limit = 2)
                        if (parts.size == 2 && parts[1].isNotBlank()) {
                            Episode(parts[0], parts[1])
                        } else if (parts.isNotEmpty() && parts[0].isNotBlank()) {
                            Episode("第${index + 1}集", parts[0])
                        } else {
                            null
                        }
                    } else {
                        Episode("第${index + 1}集", part)
                    }
                }
            } else if (url.contains("$")) {
                val parts = url.split("$", limit = 2)
                if (parts.size == 2 && parts[1].isNotBlank()) {
                    listOf(Episode(parts[0], parts[1]))
                } else if (parts.isNotEmpty() && parts[0].isNotBlank()) {
                    listOf(Episode("", parts[0]))
                } else {
                    emptyList()
                }
            } else {
                listOf(Episode("", url))
            }
        } catch (e: Exception) {
            // Fallback: treat the entire URL as a single episode
            if (url.isNotBlank()) listOf(Episode("", url)) else emptyList()
        }
    }
    
    /**
     * Episode data class
     */
    data class Episode(
        val name: String,
        val url: String
    )
}
