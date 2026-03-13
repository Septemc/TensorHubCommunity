<template>
  <el-card>
    <template #header>
      <div class="section-title">
        <span>{{ page?.title || '关于我们' }}</span>
      </div>
    </template>
    <MarkdownContent :content="page?.content || '这里将展示团队介绍、社区定位与发展方向。'" />
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