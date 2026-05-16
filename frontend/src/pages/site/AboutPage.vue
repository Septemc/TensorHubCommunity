<template>
  <div class="px-4 py-4 md:px-0 md:py-6 pb-20 lg:pb-4">
    <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
      <i class="fas fa-info-circle text-[#0064FF]"></i> {{ page?.title || '关于我们' }}
    </h2>
    <div class="content-card p-4 md:p-5 shadow-sm">
      <MarkdownContent :content="page?.content || '这里将展示团队介绍、社区定位与发展方向。'" />
    </div>
  </div>
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