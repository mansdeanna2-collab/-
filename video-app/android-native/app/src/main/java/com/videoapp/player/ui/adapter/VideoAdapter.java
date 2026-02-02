package com.videoapp.player.ui.adapter;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.PorterDuff;
import android.graphics.PorterDuffXfermode;
import android.graphics.Rect;
import android.graphics.RectF;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
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
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

/**
 * Adapter for displaying videos in a RecyclerView grid
 */
public class VideoAdapter extends ListAdapter<Video, VideoAdapter.VideoViewHolder> {

    private static final String TAG = "VideoAdapter";
    
    // Background executor for base64 image decoding
    private static final ExecutorService imageDecoder = Executors.newFixedThreadPool(2);
    private static final Handler mainHandler = new Handler(Looper.getMainLooper());

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
                    // Check if it's a data URL (base64 image)
                    if (ImageUtils.isDataUrl(formattedUrl)) {
                        // Show placeholder while decoding
                        binding.thumbnailImage.setImageResource(R.drawable.ic_video_placeholder);
                        
                        // Decode base64 on background thread to avoid ANR
                        final String dataUrl = formattedUrl;
                        final int position = getBindingAdapterPosition();
                        imageDecoder.execute(() -> {
                            try {
                                Bitmap bitmap = ImageUtils.decodeBase64Image(dataUrl);
                                if (bitmap != null) {
                                    // Apply rounded corners transformation
                                    Bitmap roundedBitmap = getRoundedCornerBitmap(bitmap, 12f);
                                    
                                    // Update UI on main thread
                                    mainHandler.post(() -> {
                                        // Check if view is still for same position (avoid recycled view issue)
                                        if (getBindingAdapterPosition() == position) {
                                            binding.thumbnailImage.setImageBitmap(roundedBitmap);
                                        }
                                        // Recycle original bitmap if different from rounded
                                        if (roundedBitmap != bitmap && !bitmap.isRecycled()) {
                                            bitmap.recycle();
                                        }
                                    });
                                }
                            } catch (Exception e) {
                                Log.e(TAG, "Error decoding base64 image", e);
                            }
                        });
                    } else {
                        // Use Coil for regular HTTP URLs
                        ImageRequest request = new ImageRequest.Builder(binding.getRoot().getContext())
                                .data(formattedUrl)
                                .crossfade(300)
                                .placeholder(R.drawable.ic_video_placeholder)
                                .error(R.drawable.ic_video_placeholder)
                                .transformations(Collections.singletonList(new RoundedCornersTransformation(12f)))
                                .size(480, 270)
                                .allowHardware(true)
                                .target(binding.thumbnailImage)
                                .build();
                        Coil.imageLoader(binding.getRoot().getContext()).enqueue(request);
                    }
                } else {
                    binding.thumbnailImage.setImageResource(R.drawable.ic_video_placeholder);
                }
            } catch (Exception e) {
                Log.e(TAG, "Error loading thumbnail", e);
                binding.thumbnailImage.setImageResource(R.drawable.ic_video_placeholder);
            }
        }
        
        /**
         * Apply rounded corners to a bitmap
         */
        @Nullable
        private Bitmap getRoundedCornerBitmap(@NonNull Bitmap bitmap, float cornerRadius) {
            try {
                int width = bitmap.getWidth();
                int height = bitmap.getHeight();
                
                Bitmap output = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888);
                Canvas canvas = new Canvas(output);
                
                Paint paint = new Paint();
                paint.setAntiAlias(true);
                
                Rect rect = new Rect(0, 0, width, height);
                RectF rectF = new RectF(rect);
                
                // Scale corner radius based on image size
                float scaledRadius = cornerRadius * (Math.min(width, height) / 100f);
                
                // Draw rounded rectangle
                canvas.drawRoundRect(rectF, scaledRadius, scaledRadius, paint);
                
                // Set xfermode to draw only inside the rounded rectangle
                paint.setXfermode(new PorterDuffXfermode(PorterDuff.Mode.SRC_IN));
                
                // Draw the bitmap
                canvas.drawBitmap(bitmap, rect, rect, paint);
                
                return output;
            } catch (Exception e) {
                Log.e(TAG, "Error creating rounded bitmap", e);
                return bitmap;
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
