<template>
  <div class="overflow-x-hidden pb-16 lg:pb-0">
    <div class="px-4 py-3 md:px-0 md:py-4">
      <div v-if="category" class="flex items-center gap-2 mb-4">
        <router-link to="/forum" class="text-[#0064FF] text-[13px]"><i class="fas fa-arrow-left mr-1"></i>返回</router-link>
        <h2 class="text-lg font-bold text-gray-900 flex items-center gap-2">
          <i :class="categoryIcon(category.type)" class="text-[#0064FF] text-[14px]"></i>
          {{ category.name }}
        </h2>
      </div>

      <div v-if="loading" class="text-center py-12 text-gray-400"><i class="fas fa-spinner fa-spin text-2xl"></i></div>

      <div v-else-if="posts.length" class="space-y-2 md:space-y-4">
        <div v-for="post in posts" :key="post.id" class="content-card p-4 md:p-5 shadow-sm">
          <div class="flex items-center gap-2 mb-3">
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

      <div v-else class="text-center py-12 text-gray-400"><i class="fas fa-inbox text-4xl mb-3"></i><p>暂无帖子</p></div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { fetchCategories, fetchCategoryPosts } from '../../api/forum'
import type { Post, Category } from '../../types/models'

const route = useRoute()
const posts = ref<Post[]>([])
const categories = ref<Category[]>([])
const category = ref<Category | null>(null)
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

function categoryIcon(type: string) {
  const icons: Record<string, string> = { forum: 'fas fa-fire-alt', contest: 'fas fa-trophy', recruit_project: 'fas fa-project-diagram', recruit_team: 'fas fa-users', notice: 'fas fa-bullhorn' }
  return icons[type] || 'fas fa-microchip'
}

onMounted(async () => {
  const catId = Number(route.params.id)
  try {
    const [c, p] = await Promise.all([fetchCategories(), fetchCategoryPosts(catId)])
    categories.value = c
    category.value = c.find(x => x.id === catId) || null
    posts.value = p
  } catch { /* ignore */ } finally { loading.value = false }
})
</script>