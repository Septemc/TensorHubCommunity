<template>
  <div class="home-page">
    <el-card class="home-hero">
      <div class="home-hero__content">
        <div class="home-hero__copy">
          <div class="home-hero__eyebrow">TensorHub Community</div>
          <h1>{{ store.homePage?.title || 'TensorHub 首页' }}</h1>
          <p class="home-hero__stats">{{ store.stats.posts || 0 }} 篇帖子正在交流中</p>
          <MarkdownContent :content="store.homePage?.content || '欢迎来到 TensorHub 社区。'" />
        </div>
        <div class="home-hero__actions">
          <el-button type="primary" size="large" @click="router.push('/forum')">进入论坛</el-button>
          <el-button plain size="large" @click="router.push('/news')">查看公告</el-button>
        </div>
      </div>
    </el-card>

    <div class="card-grid two">
      <el-card>
        <template #header>
          <div class="section-title home-section__title">
            <span>最新公告</span>
            <RouterLink to="/news">更多</RouterLink>
          </div>
        </template>
        <el-empty v-if="!store.announcements.length" description="暂无公告" />
        <div v-else class="home-list">
          <RouterLink v-for="item in store.announcements" :key="item.id" :to="`/news/${item.id}`" class="home-list__item">
            <strong>{{ item.title }}</strong>
            <span>查看详情</span>
          </RouterLink>
        </div>
      </el-card>

      <el-card>
        <template #header>
          <div class="section-title home-section__title">
            <span>热门帖子</span>
            <RouterLink to="/forum">更多</RouterLink>
          </div>
        </template>
        <el-empty v-if="!store.hotPosts.length" description="暂无帖子" />
        <div v-else class="home-list">
          <RouterLink v-for="post in store.hotPosts" :key="post.id" :to="`/forum/post/${post.id}`" class="home-list__item">
            <strong>{{ post.title }}</strong>
            <span>{{ post.likes_count }} 点赞</span>
          </RouterLink>
        </div>
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

<style scoped>
.home-page {
  display: grid;
  gap: 20px;
}

.home-hero {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.16), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.96), rgba(248, 250, 252, 0.92));
}

.home-hero__content {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.home-hero__copy {
  max-width: 720px;
}

.home-hero__eyebrow {
  display: inline-flex;
  align-items: center;
  min-height: 32px;
  padding: 0 12px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.home-hero__copy h1 {
  margin: 16px 0 12px;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.1;
}

.home-hero__stats {
  margin: 0 0 18px;
  color: #475569;
  font-size: 16px;
  font-weight: 600;
}

.home-hero__actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 156px;
}

.home-section__title {
  flex-direction: row;
  align-items: center;
}

.home-list {
  display: grid;
  gap: 12px;
}

.home-list__item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px 18px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.14);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.home-list__item:hover {
  transform: translateY(-1px);
  border-color: rgba(59, 130, 246, 0.25);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.05);
}

.home-list__item strong {
  color: #0f172a;
}

.home-list__item span {
  flex-shrink: 0;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 960px) {
  .home-hero__content {
    flex-direction: column;
  }

  .home-hero__actions {
    width: 100%;
    min-width: 0;
  }

  .home-hero__actions :deep(.el-button) {
    width: 100%;
  }
}
</style>
