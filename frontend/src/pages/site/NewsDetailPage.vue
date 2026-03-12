<template>
  <el-card v-loading="loading">
    <template #header>
      <div class="section-title"><span>{{ item?.title || '公告详情' }}</span></div>
    </template>
    <MarkdownContent v-if="item" :content="item.content" />
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import MarkdownContent from '../../components/MarkdownContent.vue'
import type { Announcement } from '../../types/models'
import { useSiteContentStore } from '../../stores/siteContent'

const route = useRoute()
const store = useSiteContentStore()
const loading = ref(false)
const item = ref<Announcement | null>(null)

onMounted(async () => {
  loading.value = true
  try {
    item.value = await store.loadAnnouncement(Number(route.params.id))
  } finally {
    loading.value = false
  }
})
</script>
