package com.videoapp.player.ui.adapter

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
        if (showAllOption && position == 0) {
            holder.bindAllOption(position == selectedPosition)
        } else {
            val adjustedPosition = if (showAllOption) position - 1 else position
            holder.bind(getItem(adjustedPosition), position == selectedPosition)
        }
    }
    
    override fun getItemCount(): Int {
        return super.getItemCount() + if (showAllOption) 1 else 0
    }
    
    fun selectCategory(position: Int) {
        val oldPosition = selectedPosition
        selectedPosition = position
        notifyItemChanged(oldPosition)
        notifyItemChanged(position)
    }
    
    inner class CategoryViewHolder(
        private val binding: ItemCategoryChipBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        
        init {
            binding.root.setOnClickListener {
                val position = bindingAdapterPosition
                if (position != RecyclerView.NO_POSITION) {
                    selectCategory(position)
                    if (showAllOption && position == 0) {
                        onCategoryClick(null)
                    } else {
                        val adjustedPosition = if (showAllOption) position - 1 else position
                        onCategoryClick(getItem(adjustedPosition))
                    }
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
