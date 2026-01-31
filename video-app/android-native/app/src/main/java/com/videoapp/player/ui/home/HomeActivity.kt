package com.videoapp.player.ui.home

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.View
import android.view.inputmethod.EditorInfo
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.widget.addTextChangedListener
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.videoapp.player.R
import com.videoapp.player.data.model.Video
import com.videoapp.player.databinding.ActivityHomeBinding
import com.videoapp.player.ui.adapter.CategoryAdapter
import com.videoapp.player.ui.adapter.VideoAdapter
import com.videoapp.player.ui.player.PlayerActivity
import com.videoapp.player.util.GridSpacingItemDecoration
import com.videoapp.player.util.HorizontalSpacingItemDecoration
import com.videoapp.player.util.KeyboardUtils
import com.videoapp.player.util.NetworkUtils

/**
 * Home Activity - displays video grid with search and category filtering
 */
class HomeActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "HomeActivity"
        private const val ITEM_SPACING_DP = 8
    }
    
    private var _binding: ActivityHomeBinding? = null
    // Safe binding getter with descriptive error message
    private val binding: ActivityHomeBinding
        get() = _binding ?: throw IllegalStateException("Binding not initialized or activity already destroyed")
    
    private val viewModel: HomeViewModel by viewModels()
    
    private var videoAdapter: VideoAdapter? = null
    private var categoryAdapter: CategoryAdapter? = null
    
    private val itemSpacingPx: Int by lazy {
        try {
            (ITEM_SPACING_DP * resources.displayMetrics.density).toInt()
        } catch (e: Exception) {
            Log.e(TAG, "Error calculating spacing", e)
            16 // Default fallback
        }
    }
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        try {
            _binding = ActivityHomeBinding.inflate(layoutInflater)
            setContentView(binding.root)
            
            setupToolbar()
            setupVideoRecyclerView()
            setupCategoryRecyclerView()
            setupSearchView()
            setupSwipeRefresh()
            observeViewModel()
        } catch (e: Exception) {
            Log.e(TAG, "Error in onCreate", e)
            Toast.makeText(this, "初始化失败，请重启应用", Toast.LENGTH_LONG).show()
        }
    }
    
    private fun setupToolbar() {
        try {
            setSupportActionBar(binding.toolbar)
            supportActionBar?.setDisplayShowTitleEnabled(false)
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up toolbar", e)
        }
    }
    
    override fun onCreateOptionsMenu(menu: Menu): Boolean {
        try {
            menuInflater.inflate(R.menu.menu_home, menu)
        } catch (e: Exception) {
            Log.e(TAG, "Error inflating menu", e)
        }
        return true
    }
    
    private fun setupVideoRecyclerView() {
        try {
            videoAdapter = VideoAdapter { video ->
                navigateToPlayer(video)
            }
            
            // Calculate span count based on screen width
            val spanCount = calculateSpanCount()
            
            binding.videoRecyclerView.apply {
                layoutManager = GridLayoutManager(this@HomeActivity, spanCount)
                adapter = videoAdapter
                
                // Add spacing decoration
                addItemDecoration(GridSpacingItemDecoration(spanCount, itemSpacingPx, true))
                
                // Enable item animator for smooth updates
                itemAnimator?.changeDuration = 150
                
                // Optimize for fixed size items
                setHasFixedSize(true)
                
                // Infinite scroll
                addOnScrollListener(object : RecyclerView.OnScrollListener() {
                    override fun onScrolled(recyclerView: RecyclerView, dx: Int, dy: Int) {
                        super.onScrolled(recyclerView, dx, dy)
                        
                        try {
                            // Only load more when scrolling down
                            if (dy <= 0) return
                            
                            val layoutManager = recyclerView.layoutManager as? GridLayoutManager
                                ?: return
                            
                            val visibleItemCount = layoutManager.childCount
                            val totalItemCount = layoutManager.itemCount
                            val firstVisibleItemPosition = layoutManager.findFirstVisibleItemPosition()
                            
                            if (viewModel.canLoadMore.value == true &&
                                viewModel.isLoading.value != true &&
                                (visibleItemCount + firstVisibleItemPosition) >= totalItemCount - 4
                            ) {
                                viewModel.loadMore()
                            }
                        } catch (e: Exception) {
                            Log.e(TAG, "Error in scroll listener", e)
                        }
                    }
                })
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up video RecyclerView", e)
        }
    }
    
    private fun calculateSpanCount(): Int {
        return try {
            val displayMetrics = resources.displayMetrics
            val screenWidthDp = displayMetrics.widthPixels / displayMetrics.density
            when {
                screenWidthDp >= 600 -> 3  // Tablet
                screenWidthDp >= 480 -> 2  // Large phone
                else -> 2                  // Normal phone
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error calculating span count", e)
            2 // Default fallback
        }
    }
    
    private fun setupCategoryRecyclerView() {
        try {
            categoryAdapter = CategoryAdapter { category ->
                viewModel.loadVideosByCategory(category?.videoCategory)
            }
            
            binding.categoryRecyclerView.apply {
                layoutManager = LinearLayoutManager(
                    this@HomeActivity,
                    LinearLayoutManager.HORIZONTAL,
                    false
                )
                adapter = categoryAdapter
                
                // Add horizontal spacing
                addItemDecoration(HorizontalSpacingItemDecoration(itemSpacingPx, false))
                
                // Optimize for fixed size items
                setHasFixedSize(true)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up category RecyclerView", e)
        }
    }
    
    private fun setupSearchView() {
        try {
            binding.searchEditText.apply {
                setOnEditorActionListener { _, actionId, _ ->
                    if (actionId == EditorInfo.IME_ACTION_SEARCH) {
                        performSearch()
                        true
                    } else {
                        false
                    }
                }
                
                addTextChangedListener { text ->
                    binding.clearSearchButton.visibility = 
                        if (text.isNullOrEmpty()) View.GONE else View.VISIBLE
                }
            }
            
            binding.searchButton.setOnClickListener {
                performSearch()
            }
            
            binding.clearSearchButton.setOnClickListener {
                binding.searchEditText.text?.clear()
                viewModel.loadInitialData()
            }
            
            // Retry button in empty view
            binding.retryButton.setOnClickListener {
                viewModel.refresh()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up search view", e)
        }
    }
    
    private fun performSearch() {
        try {
            val query = binding.searchEditText.text?.toString()?.trim() ?: ""
            if (query.isNotEmpty()) {
                // Check network connectivity
                if (!NetworkUtils.isNetworkAvailable(this)) {
                    Toast.makeText(this, NetworkUtils.getNetworkErrorMessage(this), Toast.LENGTH_SHORT).show()
                    return
                }
                
                viewModel.searchVideos(query)
                // Hide keyboard
                KeyboardUtils.hideKeyboard(this)
                binding.searchEditText.clearFocus()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error performing search", e)
        }
    }
    
    private fun setupSwipeRefresh() {
        try {
            binding.swipeRefreshLayout.setOnRefreshListener {
                viewModel.refresh()
            }
            
            // Set colors
            binding.swipeRefreshLayout.setColorSchemeResources(
                R.color.colorPrimary,
                R.color.colorAccent
            )
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up swipe refresh", e)
        }
    }
    
    private fun observeViewModel() {
        try {
            // Observe videos
            viewModel.videos.observe(this) { videos ->
                try {
                    videoAdapter?.submitList(videos)
                    updateEmptyView(videos.isEmpty() && viewModel.isLoading.value != true)
                } catch (e: Exception) {
                    Log.e(TAG, "Error updating videos", e)
                }
            }
            
            // Observe categories
            viewModel.categories.observe(this) { categories ->
                try {
                    categoryAdapter?.submitList(categories)
                } catch (e: Exception) {
                    Log.e(TAG, "Error updating categories", e)
                }
            }
            
            // Observe statistics
            viewModel.statistics.observe(this) { statistics ->
                try {
                    if (statistics != null) {
                        binding.statsText.text = getString(
                            R.string.stats_format,
                            statistics.totalVideos,
                            statistics.totalPlays
                        )
                        binding.statsText.visibility = View.VISIBLE
                    } else {
                        binding.statsText.visibility = View.GONE
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error updating statistics", e)
                }
            }
            
            // Observe loading state
            viewModel.isLoading.observe(this) { isLoading ->
                try {
                    binding.swipeRefreshLayout.isRefreshing = isLoading
                    
                    // Show loading indicator for initial load
                    val adapterItemCount = videoAdapter?.itemCount ?: 0
                    binding.loadingView.visibility = 
                        if (isLoading && adapterItemCount == 0) View.VISIBLE else View.GONE
                    
                    // Update empty view when loading completes
                    if (!isLoading) {
                        updateEmptyView(adapterItemCount == 0)
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error updating loading state", e)
                }
            }
            
            // Observe errors
            viewModel.error.observe(this) { error ->
                try {
                    if (error != null) {
                        Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
                        // Show retry button when there's an error
                        val adapterItemCount = videoAdapter?.itemCount ?: 0
                        if (adapterItemCount == 0) {
                            showErrorState(error)
                        }
                        viewModel.clearError()
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error handling error state", e)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error setting up observers", e)
        }
    }
    
    private fun updateEmptyView(isEmpty: Boolean) {
        try {
            binding.emptyView.visibility = if (isEmpty) View.VISIBLE else View.GONE
            if (isEmpty) {
                binding.emptyIcon.text = "📭"
                binding.emptyText.text = getString(R.string.no_videos)
                binding.retryButton.visibility = View.GONE
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error updating empty view", e)
        }
    }
    
    private fun showErrorState(error: String) {
        try {
            binding.emptyView.visibility = View.VISIBLE
            binding.emptyIcon.text = "⚠️"
            binding.emptyText.text = error
            binding.retryButton.visibility = View.VISIBLE
        } catch (e: Exception) {
            Log.e(TAG, "Error showing error state", e)
        }
    }
    
    private fun navigateToPlayer(video: Video) {
        try {
            val intent = Intent(this, PlayerActivity::class.java).apply {
                putExtra(PlayerActivity.EXTRA_VIDEO_ID, video.videoId)
            }
            startActivity(intent)
        } catch (e: Exception) {
            Log.e(TAG, "Error navigating to player", e)
            Toast.makeText(this, "无法打开视频", Toast.LENGTH_SHORT).show()
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Clean up binding to prevent memory leaks
        _binding = null
        videoAdapter = null
        categoryAdapter = null
    }
}
