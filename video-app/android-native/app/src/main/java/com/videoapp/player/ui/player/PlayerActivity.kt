package com.videoapp.player.ui.player

import android.content.Intent
import android.os.Bundle
import android.view.View
import android.view.WindowManager
import android.widget.Toast
import androidx.activity.viewModels
import androidx.appcompat.app.AppCompatActivity
import androidx.core.view.WindowCompat
import androidx.core.view.WindowInsetsCompat
import androidx.core.view.WindowInsetsControllerCompat
import androidx.media3.common.MediaItem
import androidx.media3.common.PlaybackException
import androidx.media3.common.Player
import androidx.media3.exoplayer.ExoPlayer
import androidx.recyclerview.widget.GridLayoutManager
import coil.load
import com.videoapp.player.R
import com.videoapp.player.data.model.Video
import com.videoapp.player.databinding.ActivityPlayerBinding
import com.videoapp.player.ui.adapter.VideoAdapter
import com.videoapp.player.util.ImageUtils

/**
 * Player Activity - full-screen video player with ExoPlayer
 */
class PlayerActivity : AppCompatActivity() {
    
    companion object {
        const val EXTRA_VIDEO_ID = "video_id"
    }
    
    private lateinit var binding: ActivityPlayerBinding
    private val viewModel: PlayerViewModel by viewModels()
    
    private var player: ExoPlayer? = null
    private var playWhenReady = true
    private var playbackPosition = 0L
    private var currentEpisodeIndex = 0
    private var hasRecordedPlay = false
    
    private lateinit var relatedAdapter: VideoAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Enable full-screen mode
        enableFullscreen()
        
        binding = ActivityPlayerBinding.inflate(layoutInflater)
        setContentView(binding.root)
        
        setupViews()
        setupRelatedVideos()
        observeViewModel()
        
        // Load video from intent
        val videoId = intent.getIntExtra(EXTRA_VIDEO_ID, 0)
        if (videoId > 0) {
            viewModel.loadVideo(videoId)
        } else {
            Toast.makeText(this, "无效的视频ID", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
    
    private fun enableFullscreen() {
        WindowCompat.setDecorFitsSystemWindows(window, false)
        
        val windowInsetsController = WindowInsetsControllerCompat(window, window.decorView)
        windowInsetsController.hide(WindowInsetsCompat.Type.systemBars())
        windowInsetsController.systemBarsBehavior = 
            WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
        
        window.addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON)
    }
    
    private fun setupViews() {
        // Back button
        binding.backButton.setOnClickListener {
            finish()
        }
        
        // Speed control
        binding.speedButton.setOnClickListener {
            showSpeedDialog()
        }
        
        // Episode buttons container (will be populated when video loads)
        binding.episodesContainer.visibility = View.GONE
    }
    
    private fun setupRelatedVideos() {
        relatedAdapter = VideoAdapter { video ->
            // Navigate to new video
            val intent = Intent(this, PlayerActivity::class.java).apply {
                putExtra(EXTRA_VIDEO_ID, video.videoId)
            }
            startActivity(intent)
            finish()
        }
        
        binding.relatedRecyclerView.apply {
            layoutManager = GridLayoutManager(this@PlayerActivity, 3)
            adapter = relatedAdapter
        }
    }
    
    private fun observeViewModel() {
        // Observe video
        viewModel.video.observe(this) { video ->
            if (video != null) {
                updateVideoInfo(video)
                setupEpisodes()
                initializePlayer()
            }
        }
        
        // Observe related videos
        viewModel.relatedVideos.observe(this) { videos ->
            relatedAdapter.submitList(videos)
            binding.relatedSection.visibility = 
                if (videos.isNotEmpty()) View.VISIBLE else View.GONE
        }
        
        // Observe loading state
        viewModel.isLoading.observe(this) { isLoading ->
            binding.loadingView.visibility = if (isLoading) View.VISIBLE else View.GONE
        }
        
        // Observe errors
        viewModel.error.observe(this) { error ->
            if (error != null) {
                Toast.makeText(this, error, Toast.LENGTH_SHORT).show()
                viewModel.clearError()
            }
        }
    }
    
    private fun updateVideoInfo(video: Video) {
        binding.videoTitleText.text = video.videoTitle
        
        // Category badge
        if (!video.videoCategory.isNullOrEmpty()) {
            binding.categoryBadge.text = video.videoCategory
            binding.categoryBadge.visibility = View.VISIBLE
        } else {
            binding.categoryBadge.visibility = View.GONE
        }
        
        // Play count
        if (video.playCount != null && video.playCount > 0) {
            binding.playCountText.text = formatPlayCount(video.playCount)
            binding.playCountText.visibility = View.VISIBLE
        } else {
            binding.playCountText.visibility = View.GONE
        }
    }
    
    private fun setupEpisodes() {
        val episodes = viewModel.getEpisodes()
        
        if (episodes.size > 1) {
            binding.episodesContainer.removeAllViews()
            
            episodes.forEachIndexed { index, episode ->
                val button = layoutInflater.inflate(
                    R.layout.item_episode_button,
                    binding.episodesContainer,
                    false
                ) as android.widget.Button
                
                button.text = episode.name.ifEmpty { "第${index + 1}集" }
                button.isSelected = index == currentEpisodeIndex
                button.setOnClickListener {
                    selectEpisode(index)
                }
                
                binding.episodesContainer.addView(button)
            }
            
            binding.episodesContainer.visibility = View.VISIBLE
        } else {
            binding.episodesContainer.visibility = View.GONE
        }
    }
    
    private fun selectEpisode(index: Int) {
        if (index == currentEpisodeIndex) return
        
        currentEpisodeIndex = index
        playbackPosition = 0L
        hasRecordedPlay = false
        
        // Update button states
        for (i in 0 until binding.episodesContainer.childCount) {
            val button = binding.episodesContainer.getChildAt(i) as android.widget.Button
            button.isSelected = i == index
        }
        
        // Play new episode
        playCurrentEpisode()
    }
    
    private fun initializePlayer() {
        if (player == null) {
            player = ExoPlayer.Builder(this)
                .build()
                .also { exoPlayer ->
                    binding.playerView.player = exoPlayer
                    
                    exoPlayer.addListener(object : Player.Listener {
                        override fun onPlaybackStateChanged(playbackState: Int) {
                            when (playbackState) {
                                Player.STATE_BUFFERING -> {
                                    binding.playerLoadingView.visibility = View.VISIBLE
                                }
                                Player.STATE_READY -> {
                                    binding.playerLoadingView.visibility = View.GONE
                                }
                                Player.STATE_ENDED -> {
                                    // Auto-play next episode
                                    val episodes = viewModel.getEpisodes()
                                    if (currentEpisodeIndex < episodes.size - 1) {
                                        selectEpisode(currentEpisodeIndex + 1)
                                    }
                                }
                                else -> {
                                    binding.playerLoadingView.visibility = View.GONE
                                }
                            }
                        }
                        
                        override fun onIsPlayingChanged(isPlaying: Boolean) {
                            // Record play count once when video starts playing
                            if (isPlaying && !hasRecordedPlay) {
                                hasRecordedPlay = true
                                viewModel.video.value?.let {
                                    viewModel.updatePlayCount(it.videoId)
                                }
                            }
                        }
                        
                        override fun onPlayerError(error: PlaybackException) {
                            binding.playerLoadingView.visibility = View.GONE
                            binding.errorView.visibility = View.VISIBLE
                            binding.errorText.text = "视频加载失败: ${error.message}"
                        }
                    })
                }
        }
        
        playCurrentEpisode()
    }
    
    private fun playCurrentEpisode() {
        val episodes = viewModel.getEpisodes()
        if (episodes.isEmpty()) return
        
        val episode = episodes.getOrNull(currentEpisodeIndex) ?: return
        
        player?.apply {
            val mediaItem = MediaItem.fromUri(episode.url)
            setMediaItem(mediaItem)
            playWhenReady = this@PlayerActivity.playWhenReady
            seekTo(playbackPosition)
            prepare()
        }
        
        binding.errorView.visibility = View.GONE
    }
    
    private fun showSpeedDialog() {
        val speeds = arrayOf("0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x")
        val speedValues = floatArrayOf(0.5f, 0.75f, 1.0f, 1.25f, 1.5f, 2.0f)
        
        val currentSpeed = player?.playbackParameters?.speed ?: 1.0f
        var selectedIndex = speedValues.indexOfFirst { it == currentSpeed }
        if (selectedIndex < 0) selectedIndex = 2 // Default to 1.0x
        
        android.app.AlertDialog.Builder(this)
            .setTitle("播放速度")
            .setSingleChoiceItems(speeds, selectedIndex) { dialog, which ->
                player?.setPlaybackSpeed(speedValues[which])
                binding.speedButton.text = speeds[which]
                dialog.dismiss()
            }
            .show()
    }
    
    private fun releasePlayer() {
        player?.let { exoPlayer ->
            playbackPosition = exoPlayer.currentPosition
            playWhenReady = exoPlayer.playWhenReady
            exoPlayer.release()
        }
        player = null
    }
    
    private fun formatPlayCount(count: Int): String {
        return when {
            count >= 10000 -> "${String.format("%.1f", count / 10000.0)}万次播放"
            else -> "${count}次播放"
        }
    }
    
    override fun onStart() {
        super.onStart()
        initializePlayer()
    }
    
    override fun onResume() {
        super.onResume()
        enableFullscreen()
        if (player == null) {
            initializePlayer()
        }
    }
    
    override fun onPause() {
        super.onPause()
        player?.pause()
    }
    
    override fun onStop() {
        super.onStop()
        releasePlayer()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        releasePlayer()
    }
}
