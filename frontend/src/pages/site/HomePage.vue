<template>
  <div class="overflow-x-hidden pb-16 lg:pb-0">
    <!-- Alert Banner -->
    <div class="bg-[#004e6d] text-white px-4 py-2 text-[12px] flex justify-between items-center border-l-4 border-cyan-400 md:rounded-sm md:my-4">
      <span class="truncate mr-2">真诚、友善、团结、专业，共建社区。</span>
      <router-link to="/about" class="underline shrink-0">《关于》</router-link>
    </div>

    <!-- Featured Section -->
    <div class="px-4 py-4 md:px-0 md:py-6">
      <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
        <i class="fas fa-fire-alt text-[#0064FF]"></i> 精选话题
      </h2>

      <!-- Loading -->
      <div v-if="loading" class="text-center py-12 text-gray-400">
        <i class="fas fa-spinner fa-spin text-2xl"></i>
      </div>

      <!-- Post List -->
      <div v-else-if="posts.length" class="space-y-2 md:space-y-4">
        <div v-for="post in posts" :key="post.id" class="content-card p-4 md:p-5 shadow-sm">
          <div class="flex items-center gap-3 mb-3">
            <router-link :to="`/forum/category/${post.category_id}`" class="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-sm border"
              :class="categoryStyle(post)">
              {{ categoryName(post) }}
            </router-link>
            <span v-if="post.is_top" class="text-[10px] px-1.5 py-0.5 rounded-sm bg-red-50 text-red-600 border border-red-100">置顶</span>
            <span v-if="post.is_essence" class="text-[10px] px-1.5 py-0.5 rounded-sm bg-yellow-50 text-yellow-600 border border-yellow-100">精华</span>
            <span class="text-[11px] text-gray-400 ml-auto">{{ timeAgo(post.created_at) }}</span>
          </div>

          <router-link :to="`/forum/post/${post.id}`" class="block">
            <h3 class="text-[15px] md:text-[17px] font-bold text-gray-900 leading-snug mb-2 hover:text-[#0064FF] transition-colors">
              {{ post.title }}
            </h3>
          </router-link>

          <div class="flex items-center gap-3 mt-3">
            <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-[11px] border border-indigo-200 shrink-0">
              {{ post.author?.username?.slice(0, 2).toUpperCase() || 'U' }}
            </div>
            <span class="text-[13px] font-medium text-gray-700">{{ post.author?.username }}</span>
            <div class="ml-auto flex items-center gap-4 text-gray-400 text-[13px]">
              <span class="flex items-center gap-1"><i class="far fa-thumbs-up"></i> {{ post.likes_count }}</span>
              <span class="flex items-center gap-1"><i class="far fa-comment"></i> {{ post.comments_count }}</span>
              <span class="flex items-center gap-1"><i class="far fa-eye"></i> {{ post.views }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12 text-gray-400">
        <i class="fas fa-inbox text-4xl mb-3"></i>
        <p>暂无帖子</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { fetchPosts } from '../../api/forum'
import type { Post } from '../../types/models'
import { fetchCategories } from '../../api/forum'
import type { Category } from '../../types/models'

const posts = ref<Post[]>([])
const categories = ref<Category[]>([])
const loading = ref(true)

function timeAgo(date?: string) {
  if (!date) return ''
  const diff = Date.now() - new Date(date).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days} 天前`
  return new Date(date).toLocaleDateString()
}

function categoryName(post: Post) {
  const cat = categories.value.find(c => c.id === post.category_id)
  return cat?.name || '话题'
}

function categoryStyle(post: Post) {
  const cat = categories.value.find(c => c.id === post.category_id)
  const type = cat?.type || 'forum'
  const styles: Record<string, string> = {
    forum: 'text-green-600 bg-green-50 border-green-100',
    contest: 'text-orange-600 bg-orange-50 border-orange-100',
    recruit_project: 'text-blue-600 bg-blue-50 border-blue-100',
    recruit_team: 'text-purple-600 bg-purple-50 border-purple-100',
    notice: 'text-red-600 bg-red-50 border-red-100',
  }
  return styles[type] || 'text-gray-600 bg-gray-50 border-gray-100'
}

onMounted(async () => {
  try {
    const [p, c] = await Promise.all([fetchPosts('latest'), fetchCategories()])
    posts.value = p
    categories.value = c
  } catch {
    // ignore
  } finally {
    loading.value = false
  }
})
</script>