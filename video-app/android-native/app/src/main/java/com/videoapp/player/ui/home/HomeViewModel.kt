package com.videoapp.player.ui.home

import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.videoapp.player.data.model.Category
import com.videoapp.player.data.model.Statistics
import com.videoapp.player.data.model.Video
import com.videoapp.player.data.repository.VideoRepository
import kotlinx.coroutines.launch

/**
 * ViewModel for HomeActivity
 */
class HomeViewModel : ViewModel() {
    
    private val repository = VideoRepository()
    
    // Videos list
    private val _videos = MutableLiveData<List<Video>>(emptyList())
    val videos: LiveData<List<Video>> = _videos
    
    // Categories list
    private val _categories = MutableLiveData<List<Category>>(emptyList())
    val categories: LiveData<List<Category>> = _categories
    
    // Statistics
    private val _statistics = MutableLiveData<Statistics?>()
    val statistics: LiveData<Statistics?> = _statistics
    
    // Loading state
    private val _isLoading = MutableLiveData(false)
    val isLoading: LiveData<Boolean> = _isLoading
    
    // Error state
    private val _error = MutableLiveData<String?>()
    val error: LiveData<String?> = _error
    
    // Pagination
    private var currentPage = 0
    private val pageSize = 20
    private var hasMorePages = true
    private var currentCategory: String? = null
    private var currentSearchQuery: String? = null
    
    // Can load more
    private val _canLoadMore = MutableLiveData(true)
    val canLoadMore: LiveData<Boolean> = _canLoadMore
    
    init {
        loadInitialData()
    }
    
    /**
     * Load initial data (videos, categories, statistics)
     */
    fun loadInitialData() {
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            // Load all data in parallel
            val videosResult = repository.getVideos(pageSize, 0)
            val categoriesResult = repository.getCategories()
            val statisticsResult = repository.getStatistics()
            
            // Process videos
            videosResult.fold(
                onSuccess = { videos ->
                    _videos.value = videos
                    hasMorePages = videos.size >= pageSize
                    _canLoadMore.value = hasMorePages
                    currentPage = 0
                },
                onFailure = { e ->
                    _error.value = e.message ?: "加载视频失败"
                }
            )
            
            // Process categories
            categoriesResult.fold(
                onSuccess = { categories ->
                    _categories.value = categories
                },
                onFailure = { /* Ignore category errors */ }
            )
            
            // Process statistics
            statisticsResult.fold(
                onSuccess = { stats ->
                    _statistics.value = stats
                },
                onFailure = { /* Ignore statistics errors */ }
            )
            
            _isLoading.value = false
        }
    }
    
    /**
     * Refresh data
     */
    fun refresh() {
        currentPage = 0
        hasMorePages = true
        _canLoadMore.value = true
        
        when {
            currentSearchQuery != null -> searchVideos(currentSearchQuery!!)
            currentCategory != null -> loadVideosByCategory(currentCategory!!)
            else -> loadInitialData()
        }
    }
    
    /**
     * Load more videos (pagination)
     */
    fun loadMore() {
        if (!hasMorePages || _isLoading.value == true) return
        
        viewModelScope.launch {
            _isLoading.value = true
            
            val offset = (currentPage + 1) * pageSize
            
            val result = when {
                currentSearchQuery != null -> repository.searchVideos(currentSearchQuery!!, pageSize, offset)
                currentCategory != null -> repository.getVideosByCategory(currentCategory!!, pageSize, offset)
                else -> repository.getVideos(pageSize, offset)
            }
            
            result.fold(
                onSuccess = { newVideos ->
                    val currentList = _videos.value ?: emptyList()
                    _videos.value = currentList + newVideos
                    hasMorePages = newVideos.size >= pageSize
                    _canLoadMore.value = hasMorePages
                    currentPage++
                },
                onFailure = { e ->
                    _error.value = e.message ?: "加载更多失败"
                }
            )
            
            _isLoading.value = false
        }
    }
    
    /**
     * Search videos by keyword
     */
    fun searchVideos(query: String) {
        currentSearchQuery = query.trim().ifEmpty { null }
        currentCategory = null
        currentPage = 0
        hasMorePages = true
        _canLoadMore.value = true
        
        if (currentSearchQuery == null) {
            loadInitialData()
            return
        }
        
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            val result = repository.searchVideos(currentSearchQuery!!, pageSize, 0)
            
            result.fold(
                onSuccess = { videos ->
                    _videos.value = videos
                    hasMorePages = videos.size >= pageSize
                    _canLoadMore.value = hasMorePages
                },
                onFailure = { e ->
                    _error.value = e.message ?: "搜索失败"
                    _videos.value = emptyList()
                }
            )
            
            _isLoading.value = false
        }
    }
    
    /**
     * Load videos by category
     */
    fun loadVideosByCategory(category: String?) {
        currentCategory = category
        currentSearchQuery = null
        currentPage = 0
        hasMorePages = true
        _canLoadMore.value = true
        
        if (category == null) {
            loadInitialData()
            return
        }
        
        viewModelScope.launch {
            _isLoading.value = true
            _error.value = null
            
            val result = repository.getVideosByCategory(category, pageSize, 0)
            
            result.fold(
                onSuccess = { videos ->
                    _videos.value = videos
                    hasMorePages = videos.size >= pageSize
                    _canLoadMore.value = hasMorePages
                },
                onFailure = { e ->
                    _error.value = e.message ?: "加载分类失败"
                    _videos.value = emptyList()
                }
            )
            
            _isLoading.value = false
        }
    }
    
    /**
     * Clear error message
     */
    fun clearError() {
        _error.value = null
    }
}
