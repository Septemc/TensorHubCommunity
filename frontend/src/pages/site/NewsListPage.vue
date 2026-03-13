<template>
  <el-card>
    <template #header>
      <div class="section-title"><span>官方讯息</span></div>
    </template>
    <el-empty v-if="!announcements.length" description="暂无公告" />
    <el-timeline v-else>
      <el-timeline-item v-for="item in announcements" :key="item.id" :timestamp="item.created_at">
        <RouterLink :to="`/news/${item.id}`">{{ item.title }}</RouterLink>
      </el-timeline-item>
    </el-timeline>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'

import { useSiteContentStore } from '../../stores/siteContent'

const store = useSiteContentStore()
const announcements = computed(() => store.announcements)

onMounted(() => {
  store.loadAnnouncements()
})
</script>