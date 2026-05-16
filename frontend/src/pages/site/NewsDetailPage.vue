<template>
  <div class="px-4 py-4 md:px-0 md:py-6 pb-20 lg:pb-4">
    <div v-if="loading" class="text-center py-12 text-gray-400"><i class="fas fa-spinner fa-spin text-2xl"></i></div>
    <template v-else-if="item">
      <div class="flex items-center gap-2 mb-3">
        <router-link to="/news" class="text-[#0064FF] text-[13px]"><i class="fas fa-arrow-left mr-1"></i>返回列表</router-link>
      </div>
      <h1 class="text-lg md:text-2xl font-bold text-gray-900 mb-2">{{ item.title }}</h1>
      <p class="text-[12px] text-gray-400 mb-4">{{ formatDate(item.created_at) }}</p>
      <div class="content-card p-4 md:p-5 shadow-sm">
        <MarkdownContent :content="item.content" />
      </div>
    </template>
    <div v-else class="text-center py-12 text-gray-400">
      <i class="fas fa-exclamation-circle text-4xl mb-3"></i>
      <p>公告不存在</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import MarkdownContent from '../../components/MarkdownContent.vue'
import type { Announcement } from '../../types/models'
import { useSiteContentStore } from '../../stores/siteContent'

const route = useRoute()
const store = useSiteContentStore()
const loading = ref(true)
const item = ref<Announcement | null>(null)

function formatDate(date?: string) {
  if (!date) return ''
  return new Date(date).toLocaleDateString()
}

onMounted(async () => {
  try {
    item.value = await store.loadAnnouncement(Number(route.params.id))
  } catch { /* ignore */ } finally { loading.value = false }
})
</script>