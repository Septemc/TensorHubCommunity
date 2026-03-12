<template>
  <div class="card-grid">
    <el-card>
      <div class="section-title">
        <div>
          <h2>{{ store.homePage?.title || 'TensorHub 社区' }}</h2>
          <p>{{ store.stats.posts || 0 }} 篇帖子正在交流中</p>
        </div>
        <el-button type="primary" @click="router.push('/forum')">进入论坛</el-button>
      </div>
      <MarkdownContent :content="store.homePage?.content || '欢迎来到 TensorHub。'" />
    </el-card>

    <div class="card-grid two">
      <el-card>
        <template #header>
          <div class="section-title">
            <span>最新公告</span>
            <RouterLink to="/news">更多</RouterLink>
          </div>
        </template>
        <el-empty v-if="!store.announcements.length" description="暂无公告" />
        <el-space v-else direction="vertical" fill>
          <el-card v-for="item in store.announcements" :key="item.id" shadow="never">
            <RouterLink :to="`/news/${item.id}`"><strong>{{ item.title }}</strong></RouterLink>
          </el-card>
        </el-space>
      </el-card>

      <el-card>
        <template #header>
          <div class="section-title">
            <span>热门帖子</span>
            <RouterLink to="/forum">更多</RouterLink>
          </div>
        </template>
        <el-empty v-if="!store.hotPosts.length" description="暂无帖子" />
        <el-space v-else direction="vertical" fill>
          <el-card v-for="post in store.hotPosts" :key="post.id" shadow="never">
            <RouterLink :to="`/forum/post/${post.id}`">{{ post.title }}</RouterLink>
          </el-card>
        </el-space>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'

import MarkdownContent from '../../components/MarkdownContent.vue'
import { useSiteContentStore } from '../../stores/siteContent'

const store = useSiteContentStore()
const router = useRouter()

onMounted(() => {
  store.loadHome()
})
</script>
