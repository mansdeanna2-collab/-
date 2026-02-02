package com.videoapp.player.ui.player;

import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.view.WindowCompat;
import androidx.core.view.WindowInsetsCompat;
import androidx.core.view.WindowInsetsControllerCompat;
import androidx.lifecycle.ViewModelProvider;
import androidx.media3.common.MediaItem;
import androidx.media3.common.PlaybackException;
import androidx.media3.common.Player;
import androidx.media3.exoplayer.ExoPlayer;
import androidx.recyclerview.widget.GridLayoutManager;

import com.videoapp.player.R;
import com.videoapp.player.data.model.Video;
import com.videoapp.player.databinding.ActivityPlayerBinding;
import com.videoapp.player.ui.adapter.VideoAdapter;
import com.videoapp.player.util.GridSpacingItemDecoration;
import com.videoapp.player.util.NetworkUtils;

import java.util.List;
import java.util.Locale;

/**
 * Player Activity - full-screen video player with ExoPlayer
 */
public class PlayerActivity extends AppCompatActivity {

    private static final String TAG = "PlayerActivity";
    public static final String EXTRA_VIDEO_ID = "video_id";
    private static final String STATE_PLAYBACK_POSITION = "playback_position";
    private static final String STATE_PLAY_WHEN_READY = "play_when_ready";
    private static final String STATE_EPISODE_INDEX = "episode_index";

    @Nullable
    private ActivityPlayerBinding binding;

    private PlayerViewModel viewModel;

    @Nullable
    private ExoPlayer player;
    @Nullable
    private Player.Listener playerListener;
    private boolean playWhenReady = true;
    private long playbackPosition = 0L;
    private int currentEpisodeIndex = 0;
    private boolean hasRecordedPlay = false;
    private boolean isPlayerInitialized = false;
    private boolean isActivityDestroyed = false;

    @Nullable
    private VideoAdapter relatedAdapter;

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        isActivityDestroyed = false;

        try {
            // Restore saved state
            if (savedInstanceState != null) {
                playbackPosition = savedInstanceState.getLong(STATE_PLAYBACK_POSITION, 0L);
                playWhenReady = savedInstanceState.getBoolean(STATE_PLAY_WHEN_READY, true);
                currentEpisodeIndex = savedInstanceState.getInt(STATE_EPISODE_INDEX, 0);
            }

            // Enable full-screen mode
            enableFullscreen();

            binding = ActivityPlayerBinding.inflate(getLayoutInflater());
            setContentView(binding.getRoot());

            viewModel = new ViewModelProvider(this).get(PlayerViewModel.class);

            setupViews();
            setupRelatedVideos();
            observeViewModel();

            // Load video from intent
            int videoId = getIntent().getIntExtra(EXTRA_VIDEO_ID, 0);
            if (videoId > 0) {
                viewModel.loadVideo(videoId);
            } else {
                Toast.makeText(this, "无效的视频ID", Toast.LENGTH_SHORT).show();
                finish();
            }
        } catch (Exception e) {
            Log.e(TAG, "Error in onCreate", e);
            Toast.makeText(this, "初始化失败", Toast.LENGTH_SHORT).show();
            finish();
        }
    }

    private void enableFullscreen() {
        try {
            WindowCompat.setDecorFitsSystemWindows(getWindow(), false);

            WindowInsetsControllerCompat windowInsetsController =
                    new WindowInsetsControllerCompat(getWindow(), getWindow().getDecorView());
            windowInsetsController.hide(WindowInsetsCompat.Type.systemBars());
            windowInsetsController.setSystemBarsBehavior(
                    WindowInsetsControllerCompat.BEHAVIOR_SHOW_TRANSIENT_BARS_BY_SWIPE
            );

            getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        } catch (Exception e) {
            Log.e(TAG, "Error enabling fullscreen", e);
        }
    }

    private void setupViews() {
        if (binding == null) return;

        try {
            // Back button
            binding.backButton.setOnClickListener(v -> finish());

            // Speed control
            binding.speedButton.setOnClickListener(v -> showSpeedDialog());

            // Retry button
            binding.retryButton.setOnClickListener(v -> {
                if (binding != null) {
                    binding.errorView.setVisibility(View.GONE);
                    binding.playerLoadingView.setVisibility(View.VISIBLE);
                }
                playCurrentEpisode();
            });

            // Episode buttons container (will be populated when video loads)
            binding.episodesContainer.setVisibility(View.GONE);
        } catch (Exception e) {
            Log.e(TAG, "Error setting up views", e);
        }
    }

    private void setupRelatedVideos() {
        if (binding == null) return;

        try {
            relatedAdapter = new VideoAdapter(video -> {
                // Navigate to new video
                Intent intent = new Intent(this, PlayerActivity.class);
                intent.putExtra(EXTRA_VIDEO_ID, video.getVideoId());
                startActivity(intent);
                finish();
            });

            int spacingPx = (int) (4 * getResources().getDisplayMetrics().density);

            binding.relatedRecyclerView.setLayoutManager(new GridLayoutManager(this, 3));
            binding.relatedRecyclerView.setAdapter(relatedAdapter);
            binding.relatedRecyclerView.addItemDecoration(new GridSpacingItemDecoration(3, spacingPx, false));
            binding.relatedRecyclerView.setHasFixedSize(true);
        } catch (Exception e) {
            Log.e(TAG, "Error setting up related videos", e);
        }
    }

    private void observeViewModel() {
        try {
            // Observe video
            viewModel.getVideo().observe(this, video -> {
                if (video != null && !isActivityDestroyed) {
                    try {
                        updateVideoInfo(video);
                        setupEpisodes();
                        if (!isPlayerInitialized) {
                            initializePlayer();
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "Error handling video update", e);
                    }
                }
            });

            // Observe related videos
            viewModel.getRelatedVideos().observe(this, videos -> {
                try {
                    if (relatedAdapter != null) {
                        relatedAdapter.submitList(videos);
                    }
                    if (binding != null) {
                        binding.relatedSection.setVisibility(
                                videos != null && !videos.isEmpty() ? View.VISIBLE : View.GONE
                        );
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error updating related videos", e);
                }
            });

            // Observe loading state
            viewModel.getIsLoading().observe(this, isLoading -> {
                try {
                    if (binding != null) {
                        binding.loadingView.setVisibility(
                                Boolean.TRUE.equals(isLoading) ? View.VISIBLE : View.GONE
                        );
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error updating loading state", e);
                }
            });

            // Observe errors
            viewModel.getError().observe(this, error -> {
                if (error != null) {
                    Toast.makeText(this, error, Toast.LENGTH_SHORT).show();
                    viewModel.clearError();
                }
            });
        } catch (Exception e) {
            Log.e(TAG, "Error setting up observers", e);
        }
    }

    private void updateVideoInfo(@NonNull Video video) {
        if (binding == null) return;

        try {
            binding.videoTitleText.setText(video.getVideoTitle());

            // Category badge
            String category = video.getVideoCategory();
            if (category != null && !category.isEmpty()) {
                binding.categoryBadge.setText(category);
                binding.categoryBadge.setVisibility(View.VISIBLE);
            } else {
                binding.categoryBadge.setVisibility(View.GONE);
            }

            // Play count
            Integer playCount = video.getPlayCount();
            if (playCount != null && playCount > 0) {
                binding.playCountText.setText(formatPlayCount(playCount));
                binding.playCountText.setVisibility(View.VISIBLE);
            } else {
                binding.playCountText.setVisibility(View.GONE);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error updating video info", e);
        }
    }

    private void setupEpisodes() {
        if (binding == null) return;

        try {
            List<PlayerViewModel.Episode> episodes = viewModel.getEpisodes();

            if (episodes.size() > 1) {
                binding.episodesContainer.removeAllViews();

                for (int index = 0; index < episodes.size(); index++) {
                    try {
                        PlayerViewModel.Episode episode = episodes.get(index);
                        View inflatedView = getLayoutInflater().inflate(
                                R.layout.item_episode_button,
                                binding.episodesContainer,
                                false
                        );

                        // Safe cast - layout should be a Button
                        if (inflatedView instanceof Button) {
                            Button button = (Button) inflatedView;
                            String name = episode.getName();
                            button.setText(name.isEmpty() ? "第" + (index + 1) + "集" : name);
                            button.setSelected(index == currentEpisodeIndex);

                            final int episodeIndex = index;
                            button.setOnClickListener(v -> selectEpisode(episodeIndex));

                            binding.episodesContainer.addView(button);
                        } else {
                            Log.w(TAG, "Episode button inflation returned unexpected type: " +
                                    (inflatedView != null ? inflatedView.getClass().getName() : "null"));
                        }
                    } catch (Exception e) {
                        Log.e(TAG, "Error creating episode button at index " + index, e);
                    }
                }

                binding.episodesContainer.setVisibility(View.VISIBLE);
            } else {
                binding.episodesContainer.setVisibility(View.GONE);
            }
        } catch (Exception e) {
            Log.e(TAG, "Error setting up episodes", e);
            if (binding != null) {
                binding.episodesContainer.setVisibility(View.GONE);
            }
        }
    }

    private void selectEpisode(int index) {
        if (binding == null) return;

        try {
            if (index == currentEpisodeIndex) return;

            currentEpisodeIndex = index;
            playbackPosition = 0L;
            hasRecordedPlay = false;

            // Update button states
            for (int i = 0; i < binding.episodesContainer.getChildCount(); i++) {
                View child = binding.episodesContainer.getChildAt(i);
                if (child instanceof Button) {
                    child.setSelected(i == index);
                }
            }

            // Play new episode
            playCurrentEpisode();
        } catch (Exception e) {
            Log.e(TAG, "Error selecting episode " + index, e);
        }
    }

    private void initializePlayer() {
        if (isActivityDestroyed || binding == null) return;

        try {
            if (player == null) {
                playerListener = new Player.Listener() {
                    @Override
                    public void onPlaybackStateChanged(int playbackState) {
                        if (isActivityDestroyed || binding == null) return;

                        try {
                            switch (playbackState) {
                                case Player.STATE_BUFFERING:
                                    binding.playerLoadingView.setVisibility(View.VISIBLE);
                                    break;
                                case Player.STATE_READY:
                                    binding.playerLoadingView.setVisibility(View.GONE);
                                    binding.errorView.setVisibility(View.GONE);
                                    break;
                                case Player.STATE_ENDED:
                                    // Auto-play next episode
                                    List<PlayerViewModel.Episode> episodes = viewModel.getEpisodes();
                                    if (currentEpisodeIndex < episodes.size() - 1) {
                                        selectEpisode(currentEpisodeIndex + 1);
                                    }
                                    break;
                                default:
                                    binding.playerLoadingView.setVisibility(View.GONE);
                                    break;
                            }
                        } catch (Exception e) {
                            Log.e(TAG, "Error in onPlaybackStateChanged", e);
                        }
                    }

                    @Override
                    public void onIsPlayingChanged(boolean isPlaying) {
                        if (isActivityDestroyed) return;

                        try {
                            // Record play count once when video starts playing
                            if (isPlaying && !hasRecordedPlay) {
                                hasRecordedPlay = true;
                                Video video = viewModel.getVideo().getValue();
                                if (video != null) {
                                    viewModel.updatePlayCount(video.getVideoId());
                                }
                            }
                        } catch (Exception e) {
                            Log.e(TAG, "Error in onIsPlayingChanged", e);
                        }
                    }

                    @Override
                    public void onPlayerError(@NonNull PlaybackException error) {
                        if (isActivityDestroyed || binding == null) return;

                        try {
                            Log.e(TAG, "Player error: " + error.errorCode, error);
                            binding.playerLoadingView.setVisibility(View.GONE);
                            binding.errorView.setVisibility(View.VISIBLE);

                            String errorMsg;
                            switch (error.errorCode) {
                                case PlaybackException.ERROR_CODE_IO_NETWORK_CONNECTION_FAILED:
                                case PlaybackException.ERROR_CODE_IO_NETWORK_CONNECTION_TIMEOUT:
                                    errorMsg = "网络连接失败，请检查网络";
                                    break;
                                case PlaybackException.ERROR_CODE_IO_FILE_NOT_FOUND:
                                    errorMsg = "视频文件不存在";
                                    break;
                                case PlaybackException.ERROR_CODE_PARSING_MANIFEST_MALFORMED:
                                case PlaybackException.ERROR_CODE_PARSING_CONTAINER_UNSUPPORTED:
                                    errorMsg = "视频格式不支持";
                                    break;
                                default:
                                    errorMsg = "视频加载失败";
                                    break;
                            }
                            binding.errorText.setText(errorMsg);
                        } catch (Exception e) {
                            Log.e(TAG, "Error handling player error", e);
                        }
                    }
                };

                // Build ExoPlayer with enhanced codec and format support
                player = new ExoPlayer.Builder(this)
                        .setHandleAudioBecomingNoisy(true)
                        // Set video scaling mode for better compatibility
                        .setVideoScalingMode(androidx.media3.common.C.VIDEO_SCALING_MODE_SCALE_TO_FIT_WITH_CROPPING)
                        // Enable decoder fallback for better hardware/software codec support
                        .setRenderersFactory(new androidx.media3.exoplayer.DefaultRenderersFactory(this)
                                .setEnableDecoderFallback(true)
                                .setExtensionRendererMode(androidx.media3.exoplayer.DefaultRenderersFactory.EXTENSION_RENDERER_MODE_PREFER))
                        .build();

                binding.playerView.setPlayer(player);
                isPlayerInitialized = true;
                player.addListener(playerListener);
            }

            playCurrentEpisode();
        } catch (Exception e) {
            Log.e(TAG, "Error initializing player", e);
            if (binding != null) {
                binding.errorView.setVisibility(View.VISIBLE);
                binding.errorText.setText("播放器初始化失败");
            }
        }
    }

    private void playCurrentEpisode() {
        if (isActivityDestroyed || binding == null || player == null) return;

        try {
            List<PlayerViewModel.Episode> episodes = viewModel.getEpisodes();
            if (episodes.isEmpty()) {
                binding.errorView.setVisibility(View.VISIBLE);
                binding.errorText.setText("没有可播放的视频");
                return;
            }

            if (currentEpisodeIndex < 0 || currentEpisodeIndex >= episodes.size()) {
                binding.errorView.setVisibility(View.VISIBLE);
                binding.errorText.setText("视频集数不存在");
                return;
            }

            PlayerViewModel.Episode episode = episodes.get(currentEpisodeIndex);

            // Validate URL before attempting to play
            if (episode.getUrl().trim().isEmpty()) {
                binding.errorView.setVisibility(View.VISIBLE);
                binding.errorText.setText("视频地址无效");
                return;
            }

            String url = episode.getUrl();
            // Check network connectivity for remote URLs
            if ((url.startsWith("http://") || url.startsWith("https://")) &&
                    !NetworkUtils.isNetworkAvailable(this)) {
                binding.errorView.setVisibility(View.VISIBLE);
                binding.errorText.setText(getString(R.string.network_error));
                return;
            }

            MediaItem mediaItem = MediaItem.fromUri(url);
            player.setMediaItem(mediaItem);
            player.setPlayWhenReady(playWhenReady);
            player.seekTo(playbackPosition);
            player.prepare();

            binding.errorView.setVisibility(View.GONE);
        } catch (Exception e) {
            Log.e(TAG, "Failed to load video: " + e.getMessage(), e);
            if (binding != null) {
                binding.errorView.setVisibility(View.VISIBLE);
                binding.errorText.setText(getString(R.string.video_load_failed));
            }
        }
    }

    private void showSpeedDialog() {
        try {
            final String[] speeds = {"0.5x", "0.75x", "1.0x", "1.25x", "1.5x", "2.0x"};
            final float[] speedValues = {0.5f, 0.75f, 1.0f, 1.25f, 1.5f, 2.0f};

            float currentSpeed = player != null ? player.getPlaybackParameters().speed : 1.0f;
            int selectedIndex = 2; // Default to 1.0x
            for (int i = 0; i < speedValues.length; i++) {
                if (speedValues[i] == currentSpeed) {
                    selectedIndex = i;
                    break;
                }
            }

            new AlertDialog.Builder(this)
                    .setTitle("播放速度")
                    .setSingleChoiceItems(speeds, selectedIndex, (dialog, which) -> {
                        try {
                            if (player != null) {
                                player.setPlaybackSpeed(speedValues[which]);
                            }
                            if (binding != null) {
                                binding.speedButton.setText(speeds[which]);
                            }
                        } catch (Exception e) {
                            Log.e(TAG, "Error setting playback speed", e);
                        }
                        dialog.dismiss();
                    })
                    .show();
        } catch (Exception e) {
            Log.e(TAG, "Error showing speed dialog", e);
        }
    }

    private void releasePlayer() {
        try {
            if (player != null) {
                playbackPosition = player.getCurrentPosition();
                playWhenReady = player.getPlayWhenReady();
                if (playerListener != null) {
                    player.removeListener(playerListener);
                }
                player.release();
            }
        } catch (Exception e) {
            Log.e(TAG, "Error releasing player", e);
        } finally {
            player = null;
            playerListener = null;
            isPlayerInitialized = false;
        }
    }

    @Override
    protected void onSaveInstanceState(@NonNull Bundle outState) {
        super.onSaveInstanceState(outState);
        try {
            if (player != null) {
                outState.putLong(STATE_PLAYBACK_POSITION, player.getCurrentPosition());
                outState.putBoolean(STATE_PLAY_WHEN_READY, player.getPlayWhenReady());
            }
            outState.putInt(STATE_EPISODE_INDEX, currentEpisodeIndex);
        } catch (Exception e) {
            Log.e(TAG, "Error saving instance state", e);
        }
    }

    @NonNull
    private String formatPlayCount(int count) {
        try {
            if (count >= 10000) {
                return String.format(Locale.getDefault(), "%.1f万次播放", count / 10000.0);
            } else {
                return count + "次播放";
            }
        } catch (Exception e) {
            return count + "次播放";
        }
    }

    @Override
    protected void onStart() {
        super.onStart();
        try {
            // Only initialize if we have video data
            Video video = viewModel.getVideo().getValue();
            if (video != null && !isPlayerInitialized && !isActivityDestroyed) {
                initializePlayer();
            }
        } catch (Exception e) {
            Log.e(TAG, "Error in onStart", e);
        }
    }

    @Override
    protected void onResume() {
        super.onResume();
        try {
            enableFullscreen();
            // Only resume playback if player exists and was playing
            if (player != null && playWhenReady && !isActivityDestroyed) {
                player.play();
            }
        } catch (Exception e) {
            Log.e(TAG, "Error in onResume", e);
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        try {
            // Save state before pausing
            if (player != null) {
                playbackPosition = player.getCurrentPosition();
                playWhenReady = player.getPlayWhenReady();
                player.pause();
            }
        } catch (Exception e) {
            Log.e(TAG, "Error in onPause", e);
        }
    }

    @Override
    protected void onStop() {
        super.onStop();
        releasePlayer();
    }

    @Override
    protected void onDestroy() {
        isActivityDestroyed = true;
        super.onDestroy();

        try {
            // Ensure player is fully released
            releasePlayer();

            // Clean up binding
            binding = null;
            relatedAdapter = null;
        } catch (Exception e) {
            Log.e(TAG, "Error in onDestroy", e);
        }
    }
}
