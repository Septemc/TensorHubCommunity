<template>
  <el-card>
    <template #header>
      <div class="section-title">
        <span>{{ page?.title || '团队介绍' }}</span>
      </div>
    </template>
    <MarkdownContent :content="page?.content || '加载中...'"></MarkdownContent>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'

import MarkdownContent from '../../components/MarkdownContent.vue'
import { useSiteContentStore } from '../../stores/siteContent'

const store = useSiteContentStore()
const page = computed(() => store.pages.about)

onMounted(() => {
  store.loadPage('about')
})
</script>
