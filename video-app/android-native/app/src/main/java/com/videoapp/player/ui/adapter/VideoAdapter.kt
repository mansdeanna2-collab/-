package com.videoapp.player.ui.adapter

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import coil.load
import coil.transform.RoundedCornersTransformation
import com.videoapp.player.R
import com.videoapp.player.data.model.Video
import com.videoapp.player.databinding.ItemVideoCardBinding
import com.videoapp.player.util.ImageUtils

/**
 * Adapter for displaying videos in a RecyclerView grid
 */
class VideoAdapter(
    private val onVideoClick: (Video) -> Unit
) : ListAdapter<Video, VideoAdapter.VideoViewHolder>(VideoDiffCallback()) {
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): VideoViewHolder {
        val binding = ItemVideoCardBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return VideoViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: VideoViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
    
    inner class VideoViewHolder(
        private val binding: ItemVideoCardBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        init {
            binding.root.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    onVideoClick(getItem(position))
                }
            }
        }
        
        fun bind(video: Video) {
            binding.apply {
                // Title
                titleText.text = video.videoTitle
                
                // Category badge
                if (!video.videoCategory.isNullOrEmpty()) {
                    categoryBadge.text = video.videoCategory
                    categoryBadge.visibility = View.VISIBLE
                } else {
                    categoryBadge.visibility = View.GONE
                }
                
                // Play count
                if (video.playCount != null && video.playCount > 0) {
                    playCountText.text = formatPlayCount(video.playCount)
                    playCountText.visibility = View.VISIBLE
                } else {
                    playCountText.visibility = View.GONE
                }
                
                // Duration
                if (!video.videoDuration.isNullOrEmpty()) {
                    durationText.text = video.videoDuration
                    durationText.visibility = View.VISIBLE
                } else {
                    durationText.visibility = View.GONE
                }
                
                // Coins badge
                if (video.videoCoins != null && video.videoCoins > 0) {
                    coinsBadge.text = "🪙 ${video.videoCoins}"
                    coinsBadge.visibility = View.VISIBLE
                } else {
                    coinsBadge.visibility = View.GONE
                }
                
                // Thumbnail image with size optimization
                val imageUrl = ImageUtils.formatImageUrl(video.videoImage)
                if (imageUrl.isNotEmpty()) {
                    try {
                        thumbnailImage.load(imageUrl) {
                            crossfade(300)
                            placeholder(R.drawable.ic_video_placeholder)
                            error(R.drawable.ic_video_placeholder)
                            transformations(RoundedCornersTransformation(12f))
                            // Limit memory usage by setting size
                            size(480, 270)
                            // Allow hardware acceleration
                            allowHardware(true)
                        }
                    } catch (e: Exception) {
                        thumbnailImage.setImageResource(R.drawable.ic_video_placeholder)
                    }
                } else {
                    thumbnailImage.setImageResource(R.drawable.ic_video_placeholder)
                }
            }
        }
        
        private fun formatPlayCount(count: Int): String {
            return when {
                count >= 10000 -> "${String.format("%.1f", count / 10000.0)}万次播放"
                else -> "${count}次播放"
            }
        }
    }
    
    /**
     * DiffUtil callback for efficient list updates
     */
    class VideoDiffCallback : DiffUtil.ItemCallback<Video>() {
        override fun areItemsTheSame(oldItem: Video, newItem: Video): Boolean {
            return oldItem.videoId == newItem.videoId
        }
        
        override fun areContentsTheSame(oldItem: Video, newItem: Video): Boolean {
            return oldItem == newItem
        }
    }
}
