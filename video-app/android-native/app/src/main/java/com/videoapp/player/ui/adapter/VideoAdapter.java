package com.videoapp.player.ui.adapter;

import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.DiffUtil;
import androidx.recyclerview.widget.ListAdapter;
import androidx.recyclerview.widget.RecyclerView;

import coil.Coil;
import coil.request.ImageRequest;
import coil.transform.RoundedCornersTransformation;

import com.videoapp.player.R;
import com.videoapp.player.data.model.Video;
import com.videoapp.player.databinding.ItemVideoCardBinding;
import com.videoapp.player.util.ImageUtils;

import java.util.Collections;
import java.util.Locale;

/**
 * Adapter for displaying videos in a RecyclerView grid
 */
public class VideoAdapter extends ListAdapter<Video, VideoAdapter.VideoViewHolder> {

    private static final String TAG = "VideoAdapter";

    public interface OnVideoClickListener {
        void onVideoClick(Video video);
    }

    private final OnVideoClickListener onVideoClick;

    public VideoAdapter(@NonNull OnVideoClickListener onVideoClick) {
        super(new VideoDiffCallback());
        this.onVideoClick = onVideoClick;
    }

    @NonNull
    @Override
    public VideoViewHolder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        ItemVideoCardBinding binding = ItemVideoCardBinding.inflate(
                LayoutInflater.from(parent.getContext()),
                parent,
                false
        );
        return new VideoViewHolder(binding);
    }

    @Override
    public void onBindViewHolder(@NonNull VideoViewHolder holder, int position) {
        try {
            // Bounds check before getting item
            if (position >= 0 && position < getItemCount()) {
                holder.bind(getItem(position));
            }
        } catch (Exception e) {
            Log.e(TAG, "Error binding video at position " + position, e);
        }
    }

    class VideoViewHolder extends RecyclerView.ViewHolder {

        private final ItemVideoCardBinding binding;

        VideoViewHolder(@NonNull ItemVideoCardBinding binding) {
            super(binding.getRoot());
            this.binding = binding;

            binding.getRoot().setOnClickListener(v -> {
                try {
                    int position = getBindingAdapterPosition();
                    if (position != RecyclerView.NO_POSITION && position < getItemCount()) {
                        onVideoClick.onVideoClick(getItem(position));
                    }
                } catch (Exception e) {
                    Log.e(TAG, "Error handling video click", e);
                }
            });
        }

        void bind(@NonNull Video video) {
            try {
                // Title
                binding.titleText.setText(video.getVideoTitle());

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

                // Duration
                String duration = video.getVideoDuration();
                if (duration != null && !duration.isEmpty()) {
                    binding.durationText.setText(duration);
                    binding.durationText.setVisibility(View.VISIBLE);
                } else {
                    binding.durationText.setVisibility(View.GONE);
                }

                // Coins badge
                Integer coins = video.getVideoCoins();
                if (coins != null && coins > 0) {
                    binding.coinsBadge.setText("🪙 " + coins);
                    binding.coinsBadge.setVisibility(View.VISIBLE);
                } else {
                    binding.coinsBadge.setVisibility(View.GONE);
                }

                // Thumbnail image with size optimization
                loadThumbnail(video.getVideoImage());
            } catch (Exception e) {
                Log.e(TAG, "Error binding video: " + video.getVideoId(), e);
                // Set fallback values
                binding.titleText.setText(video.getVideoTitle());
                binding.thumbnailImage.setImageResource(R.drawable.ic_video_placeholder);
            }
        }

        private void loadThumbnail(String imageUrl) {
            try {
                String formattedUrl = ImageUtils.formatImageUrl(imageUrl);
                if (!formattedUrl.isEmpty()) {
                    ImageRequest request = new ImageRequest.Builder(binding.getRoot().getContext())
                            .data(formattedUrl)
                            .crossfade(300)
                            .placeholder(R.drawable.ic_video_placeholder)
                            .error(R.drawable.ic_video_placeholder)
                            .transformations(Collections.singletonList(new RoundedCornersTransformation(12f)))
                            .size(480, 270)
                            .allowHardware(true)
                            .target(binding.thumbnailImage)
                            .listener(
                                    request1 -> null,
                                    (request1, result) -> null,
                                    (request1, throwable) -> {
                                        Log.d(TAG, "Image load error: " + throwable.getMessage());
                                        return null;
                                    }
                            )
                            .build();
                    Coil.imageLoader(binding.getRoot().getContext()).enqueue(request);
                } else {
                    binding.thumbnailImage.setImageResource(R.drawable.ic_video_placeholder);
                }
            } catch (Exception e) {
                Log.e(TAG, "Error loading thumbnail", e);
                binding.thumbnailImage.setImageResource(R.drawable.ic_video_placeholder);
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
    }

    /**
     * DiffUtil callback for efficient list updates
     */
    static class VideoDiffCallback extends DiffUtil.ItemCallback<Video> {
        @Override
        public boolean areItemsTheSame(@NonNull Video oldItem, @NonNull Video newItem) {
            return oldItem.getVideoId() == newItem.getVideoId();
        }

        @Override
        public boolean areContentsTheSame(@NonNull Video oldItem, @NonNull Video newItem) {
            return oldItem.equals(newItem);
        }
    }
}
