package com.videoapp.player.ui.adapter

import android.util.Log
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.recyclerview.widget.DiffUtil
import androidx.recyclerview.widget.ListAdapter
import androidx.recyclerview.widget.RecyclerView
import com.videoapp.player.data.model.Category
import com.videoapp.player.databinding.ItemCategoryChipBinding

/**
 * Adapter for displaying categories as chips
 */
class CategoryAdapter(
    private val onCategoryClick: (Category?) -> Unit
) : ListAdapter<Category, CategoryAdapter.CategoryViewHolder>(CategoryDiffCallback()) {
    
    companion object {
        private const val TAG = "CategoryAdapter"
    }
    
    private var selectedPosition = 0
    private var showAllOption = true
    
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): CategoryViewHolder {
        val binding = ItemCategoryChipBinding.inflate(
            LayoutInflater.from(parent.context),
            parent,
            false
        )
        return CategoryViewHolder(binding)
    }
    
    override fun onBindViewHolder(holder: CategoryViewHolder, position: Int) {
        try {
            if (showAllOption && position == 0) {
                holder.bindAllOption(position == selectedPosition)
            } else {
                val adjustedPosition = if (showAllOption) position - 1 else position
                val itemCount = super.getItemCount()
                
                // Bounds check to prevent IndexOutOfBoundsException
                if (adjustedPosition >= 0 && adjustedPosition < itemCount) {
                    holder.bind(getItem(adjustedPosition), position == selectedPosition)
                } else {
                    // Fallback to "All" option if position is out of bounds
                    Log.w(TAG, "Position $adjustedPosition out of bounds (count: $itemCount), showing fallback")
                    holder.bindAllOption(false)
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error binding category at position $position", e)
            // Safe fallback
            holder.bindAllOption(false)
        }
    }
    
    override fun getItemCount(): Int {
        return super.getItemCount() + if (showAllOption) 1 else 0
    }
    
    fun selectCategory(position: Int) {
        try {
            val oldPosition = selectedPosition
            selectedPosition = position
            
            // Validate positions before notifying
            val totalCount = itemCount
            if (oldPosition in 0 until totalCount) {
                notifyItemChanged(oldPosition)
            }
            if (position in 0 until totalCount) {
                notifyItemChanged(position)
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error selecting category at position $position", e)
        }
    }
    
    inner class CategoryViewHolder(
        private val binding: ItemCategoryChipBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        init {
            binding.root.setOnClickListener {
                try {
                    val position = bindingAdapterPosition
                    if (position != RecyclerView.NO_POSITION) {
                        selectCategory(position)
                        if (showAllOption && position == 0) {
                            onCategoryClick(null)
                        } else {
                            val adjustedPosition = if (showAllOption) position - 1 else position
                            val itemCount = this@CategoryAdapter.currentList.size
                            
                            if (adjustedPosition >= 0 && adjustedPosition < itemCount) {
                                onCategoryClick(getItem(adjustedPosition))
                            } else {
                                // If out of bounds, treat as "All" category
                                onCategoryClick(null)
                            }
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error handling category click", e)
                    // Fallback to "All" on error
                    onCategoryClick(null)
                }
            }
        }
        
        fun bind(category: Category, isSelected: Boolean) {
            binding.apply {
                categoryName.text = category.videoCategory
                categoryCount.text = "(${category.videoCount})"
                categoryCount.visibility = View.VISIBLE
                
                updateSelection(isSelected)
            }
        }
        
        fun bindAllOption(isSelected: Boolean) {
            binding.apply {
                categoryName.text = itemView.context.getString(com.videoapp.player.R.string.all_categories)
                categoryCount.visibility = View.GONE
                
                updateSelection(isSelected)
            }
        }
        
        private fun updateSelection(isSelected: Boolean) {
            binding.root.isSelected = isSelected
            binding.root.alpha = if (isSelected) 1.0f else 0.7f
        }
    }
    
    /**
     * DiffUtil callback for efficient list updates
     */
    class CategoryDiffCallback : DiffUtil.ItemCallback<Category>() {
        override fun areItemsTheSame(oldItem: Category, newItem: Category): Boolean {
            return oldItem.videoCategory == newItem.videoCategory
        }
        
        override fun areContentsTheSame(oldItem: Category, newItem: Category): Boolean {
            return oldItem == newItem
        }
    }
}
