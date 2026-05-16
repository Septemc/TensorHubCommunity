<template>
  <div class="px-4 py-4 md:px-0 md:py-6 pb-20 lg:pb-4">
    <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
      <i class="fas fa-bullhorn text-[#0064FF]"></i> 官方讯息
    </h2>

    <div v-if="!announcements.length" class="content-card p-8 text-center shadow-sm">
      <i class="fas fa-inbox text-3xl text-gray-300 mb-3"></i>
      <p class="text-gray-400 text-[14px]">暂无公告</p>
    </div>

    <div v-else class="space-y-2 md:space-y-3">
      <router-link v-for="item in announcements" :key="item.id" :to="`/news/${item.id}`"
        class="block content-card p-4 md:p-5 shadow-sm hover:border-[#0064FF]/30 transition-colors group">
        <div class="flex items-start justify-between gap-3">
          <div>
            <h3 class="text-[15px] md:text-[16px] font-bold text-gray-900 group-hover:text-[#0064FF] transition-colors">{{ item.title }}</h3>
            <p v-if="item.content" class="text-[13px] text-gray-400 mt-1 line-clamp-1">{{ stripHtml(item.content) }}</p>
          </div>
          <span class="text-[11px] text-gray-400 shrink-0 mt-1">{{ formatDate(item.created_at) }}</span>
        </div>
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useSiteContentStore } from '../../stores/siteContent'
import { stripHtml } from '../../utils/content'

const store = useSiteContentStore()
const announcements = computed(() => store.announcements)

function formatDate(date?: string) {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

onMounted(() => {
  store.loadAnnouncements()
})
</script>