<template>
  <div class="overflow-x-hidden pb-16 lg:pb-0">
    <!-- Sort Tabs -->
    <div class="px-4 py-3 md:px-0 flex items-center gap-2 border-b border-gray-100">
      <button v-for="s in sorts" :key="s.value" @click="sort = s.value"
        class="px-3 py-1 rounded-sm text-[13px] font-medium transition-all"
        :class="sort === s.value ? 'bg-[#0064FF] text-white' : 'text-gray-500 hover:bg-gray-100'">
        {{ s.label }}
      </button>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="text-center py-12 text-gray-400">
      <i class="fas fa-spinner fa-spin text-2xl"></i>
    </div>

    <!-- Post List -->
    <div v-else-if="posts.length" class="space-y-2 md:space-y-4 p-4 md:p-0 md:py-4">
      <div v-for="post in posts" :key="post.id" class="content-card p-4 md:p-5 shadow-sm">
        <div class="flex items-center gap-2 mb-3">
          <router-link :to="`/forum/category/${post.category_id}`" class="text-[10px] px-1.5 py-0.5 rounded-sm border"
            :class="categoryColor(post)">
            {{ categoryName(post) }}
          </router-link>
          <span v-if="post.is_top" class="text-[10px] px-1.5 py-0.5 rounded-sm bg-red-50 text-red-600 border border-red-100">置顶</span>
          <span v-if="post.is_essence" class="text-[10px] px-1.5 py-0.5 rounded-sm bg-yellow-50 text-yellow-600 border border-yellow-100">精华</span>
          <span class="text-[11px] text-gray-400 ml-auto">{{ timeAgo(post.created_at) }}</span>
        </div>
        <router-link :to="`/forum/post/${post.id}`" class="block">
          <h3 class="text-[15px] md:text-[17px] font-bold text-gray-900 leading-snug mb-2 hover:text-[#0064FF] transition-colors">{{ post.title }}</h3>
        </router-link>
        <div class="flex items-center gap-3 mt-3">
          <div class="w-8 h-8 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-[11px] border border-indigo-200 shrink-0">
            {{ post.author?.username?.slice(0, 2).toUpperCase() || 'U' }}
          </div>
          <span class="text-[13px] font-medium text-gray-700">{{ post.author?.username }}</span>
          <div class="ml-auto flex items-center gap-4 text-gray-400 text-[13px]">
            <span class="flex items-center gap-1"><i class="far fa-thumbs-up"></i> {{ post.likes_count }}</span>
            <span class="flex items-center gap-1"><i class="far fa-comment"></i> {{ post.comments_count }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="text-center py-12 text-gray-400">
      <i class="fas fa-inbox text-4xl mb-3"></i>
      <p>暂无帖子</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { fetchPosts, fetchCategories } from '../../api/forum'
import type { Post, Category } from '../../types/models'

const posts = ref<Post[]>([])
const categories = ref<Category[]>([])
const loading = ref(true)
const sort = ref('latest')
const sorts = [
  { label: '最新', value: 'latest' },
  { label: '热门', value: 'hot' },
  { label: '精华', value: 'essence' },
]

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
  return categories.value.find(c => c.id === post.category_id)?.name || '话题'
}

function categoryColor(post: Post) {
  const type = categories.value.find(c => c.id === post.category_id)?.type || 'forum'
  const s: Record<string, string> = {
    forum: 'text-green-600 bg-green-50 border-green-100',
    contest: 'text-orange-600 bg-orange-50 border-orange-100',
    recruit_project: 'text-blue-600 bg-blue-50 border-blue-100',
    recruit_team: 'text-purple-600 bg-purple-50 border-purple-100',
    notice: 'text-red-600 bg-red-50 border-red-100',
  }
  return s[type] || 'text-gray-600 bg-gray-50 border-gray-100'
}

async function load() {
  loading.value = true
  try {
    posts.value = await fetchPosts(sort.value)
  } catch { /* ignore */ } finally { loading.value = false }
}

watch(sort, load)
onMounted(async () => {
  try { categories.value = await fetchCategories() } catch { /* ignore */ }
  load()
})
</script>