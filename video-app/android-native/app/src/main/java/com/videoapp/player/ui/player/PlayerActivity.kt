package com.videoapp.player.ui.player

import android.content.Intent
import android.os.Bundle
import android.util.Log
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
import com.videoapp.player.R
import com.videoapp.player.data.model.Video
import com.videoapp.player.databinding.ActivityPlayerBinding
import com.videoapp.player.ui.adapter.VideoAdapter
import com.videoapp.player.util.GridSpacingItemDecoration
import com.videoapp.player.util.NetworkUtils

/**
 * Player Activity - full-screen video player with ExoPlayer
 */
class PlayerActivity : AppCompatActivity() {
    
    companion object {
        const val EXTRA_VIDEO_ID = "video_id"
        private const val STATE_PLAYBACK_POSITION = "playback_position"
        private const val STATE_PLAY_WHEN_READY = "play_when_ready"
        private const val STATE_EPISODE_INDEX = "episode_index"
    }
    
    private lateinit var binding: ActivityPlayerBinding
    private val viewModel: PlayerViewModel by viewModels()
    
    private var player: ExoPlayer? = null
    private var playerListener: Player.Listener? = null
    private var playWhenReady = true
    private var playbackPosition = 0L
    private var currentEpisodeIndex = 0
    private var hasRecordedPlay = false
    private var isPlayerInitialized = false
    
    private lateinit var relatedAdapter: VideoAdapter
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Restore saved state
        savedInstanceState?.let {
            playbackPosition = it.getLong(STATE_PLAYBACK_POSITION, 0L)
            playWhenReady = it.getBoolean(STATE_PLAY_WHEN_READY, true)
            currentEpisodeIndex = it.getInt(STATE_EPISODE_INDEX, 0)
        }
        
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
        
        // Retry button
        binding.retryButton.setOnClickListener {
            binding.errorView.visibility = View.GONE
            binding.playerLoadingView.visibility = View.VISIBLE
            playCurrentEpisode()
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
        
        val spacingPx = (4 * resources.displayMetrics.density).toInt()
        
        binding.relatedRecyclerView.apply {
            layoutManager = GridLayoutManager(this@PlayerActivity, 3)
            adapter = relatedAdapter
            addItemDecoration(GridSpacingItemDecoration(3, spacingPx, false))
            setHasFixedSize(true)
        }
    }
    
    private fun observeViewModel() {
        // Observe video
        viewModel.video.observe(this) { video ->
            if (video != null) {
                updateVideoInfo(video)
                setupEpisodes()
                if (!isPlayerInitialized) {
                    initializePlayer()
                }
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
            playerListener = object : Player.Listener {
                override fun onPlaybackStateChanged(playbackState: Int) {
                    when (playbackState) {
                        Player.STATE_BUFFERING -> {
                            binding.playerLoadingView.visibility = View.VISIBLE
                        }
                        Player.STATE_READY -> {
                            binding.playerLoadingView.visibility = View.GONE
                            binding.errorView.visibility = View.GONE
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
                    val errorMsg = when (error.errorCode) {
                        PlaybackException.ERROR_CODE_IO_NETWORK_CONNECTION_FAILED,
                        PlaybackException.ERROR_CODE_IO_NETWORK_CONNECTION_TIMEOUT ->
                            "网络连接失败，请检查网络"
                        PlaybackException.ERROR_CODE_IO_FILE_NOT_FOUND ->
                            "视频文件不存在"
                        PlaybackException.ERROR_CODE_PARSING_MANIFEST_MALFORMED,
                        PlaybackException.ERROR_CODE_PARSING_CONTAINER_UNSUPPORTED ->
                            "视频格式不支持"
                        else -> "视频加载失败"
                    }
                    binding.errorText.text = errorMsg
                }
            }
            
            player = ExoPlayer.Builder(this)
                .setHandleAudioBecomingNoisy(true)
                .build()
                .also { exoPlayer ->
                    binding.playerView.player = exoPlayer
                    isPlayerInitialized = true
                    playerListener?.let { exoPlayer.addListener(it) }
                }
        }
        
        playCurrentEpisode()
    }
    
    private fun playCurrentEpisode() {
        val episodes = viewModel.getEpisodes()
        if (episodes.isEmpty()) {
            binding.errorView.visibility = View.VISIBLE
            binding.errorText.text = "没有可播放的视频"
            return
        }
        
        val episode = episodes.getOrNull(currentEpisodeIndex) ?: run {
            binding.errorView.visibility = View.VISIBLE
            binding.errorText.text = "视频集数不存在"
            return
        }
        
        // Validate URL before attempting to play
        if (episode.url.isBlank()) {
            binding.errorView.visibility = View.VISIBLE
            binding.errorText.text = "视频地址无效"
            return
        }
        
        // Check network connectivity for remote URLs
        if ((episode.url.startsWith("http://") || episode.url.startsWith("https://")) 
            && !NetworkUtils.isNetworkAvailable(this)) {
            binding.errorView.visibility = View.VISIBLE
            binding.errorText.text = getString(R.string.network_error)
            return
        }
        
        try {
            player?.apply {
                val mediaItem = MediaItem.fromUri(episode.url)
                setMediaItem(mediaItem)
                playWhenReady = this@PlayerActivity.playWhenReady
                seekTo(playbackPosition)
                prepare()
            }
            
            binding.errorView.visibility = View.GONE
        } catch (e: Exception) {
            Log.e("PlayerActivity", "Failed to load video: ${e.message}", e)
            binding.errorView.visibility = View.VISIBLE
            binding.errorText.text = getString(R.string.video_load_failed)
        }
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
            playerListener?.let { listener ->
                exoPlayer.removeListener(listener)
            }
            exoPlayer.release()
        }
        player = null
        playerListener = null
        isPlayerInitialized = false
    }
    
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        player?.let {
            outState.putLong(STATE_PLAYBACK_POSITION, it.currentPosition)
            outState.putBoolean(STATE_PLAY_WHEN_READY, it.playWhenReady)
        }
        outState.putInt(STATE_EPISODE_INDEX, currentEpisodeIndex)
    }
    
    private fun formatPlayCount(count: Int): String {
        return when {
            count >= 10000 -> "${String.format("%.1f", count / 10000.0)}万次播放"
            else -> "${count}次播放"
        }
    }
    
    override fun onStart() {
        super.onStart()
        // Only initialize if we have video data
        if (viewModel.video.value != null && !isPlayerInitialized) {
            initializePlayer()
        }
    }
    
    override fun onResume() {
        super.onResume()
        enableFullscreen()
        // Only resume playback if player exists and was playing
        if (player != null && playWhenReady) {
            player?.play()
        }
    }
    
    override fun onPause() {
        super.onPause()
        // Save state before pausing
        player?.let {
            playbackPosition = it.currentPosition
            playWhenReady = it.playWhenReady
            it.pause()
        }
    }
    
    override fun onStop() {
        super.onStop()
        releasePlayer()
    }
    
    override fun onDestroy() {
        super.onDestroy()
        // Ensure player is fully released
        releasePlayer()
    }
}
