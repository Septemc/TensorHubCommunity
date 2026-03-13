<template>
  <div class="forum-home">
    <el-card class="forum-home__hero">
      <div class="forum-home__hero-top">
        <div class="forum-home__hero-copy">
          <div class="forum-home__eyebrow">Forum Hub</div>
          <h1>论坛广场</h1>
          <p>围绕竞赛、项目、组队与日常技术交流，快速找到你关心的话题和协作者。</p>
        </div>

        <div class="forum-home__hero-actions">
          <el-button type="primary" size="large" @click="router.push(auth.isVerified ? '/forum/create' : '/login')">
            {{ auth.isVerified ? '发布帖子' : '登录参与' }}
          </el-button>
          <el-button plain size="large" @click="router.push('/news')">查看公告</el-button>
          <el-button text size="large" @click="router.push('/forum')">进入论坛</el-button>
        </div>
      </div>

      <div class="forum-home__hero-stats">
        <div class="forum-home__hero-stat">
          <span>讨论板块</span>
          <strong>{{ categories.length }}</strong>
          <small>覆盖讨论、竞赛、项目招募与组队招募</small>
        </div>
        <div class="forum-home__hero-stat">
          <span>动态帖子</span>
          <strong>{{ posts.length }}</strong>
          <small>支持按最新与最热自由切换浏览</small>
        </div>
      </div>
    </el-card>

    <el-card class="forum-home__boards-card">
      <div class="forum-home__board-grid">
        <RouterLink
          v-for="item in categories"
          :key="item.id"
          :to="`/forum/category/${item.id}`"
          class="forum-home__board-pill"
        >
          <span class="forum-home__board-name">{{ item.name }}</span>
          <span class="forum-home__board-count">{{ item.posts_count }}</span>
        </RouterLink>
      </div>
    </el-card>

    <el-card class="forum-home__posts-card">
      <template #header>
        <div class="section-title forum-home__posts-head">
          <div>
            <span class="forum-home__posts-title">帖子流</span>
            <p class="forum-home__posts-subtitle">预览展示正文渲染后的第一句话，便于快速判断内容主题。</p>
          </div>
          <el-segmented v-model="sort" :options="sortOptions" @change="loadPosts" />
        </div>
      </template>

      <el-empty v-if="!posts.length" description="暂无帖子" />
      <div v-else class="forum-home__post-list">
        <RouterLink v-for="item in posts" :key="item.id" :to="`/forum/post/${item.id}`" class="forum-home__post-card">
          <div class="forum-home__post-top">
            <div class="forum-home__post-badges">
              <span v-if="item.is_top" class="forum-pill forum-pill--top">置顶</span>
              <span v-if="item.is_essence" class="forum-pill forum-pill--essence">精华</span>
              <span class="forum-home__post-type">{{ postTypeLabel(item.post_type) }}</span>
            </div>
            <RoleTag :user="item.author" />
          </div>
          <h3>{{ item.title }}</h3>
          <p class="forum-home__post-excerpt">{{ getFirstSentence(item.content) }}</p>
          <div class="forum-home__post-bottom">
            <span>{{ item.author.username }}</span>
            <span>点赞 {{ item.likes_count }}</span>
            <span>评论 {{ item.comments_count }}</span>
            <span>浏览 {{ item.views }}</span>
          </div>
        </RouterLink>
      </div>
    </el-card>

    <ForumBackTopButton />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'

import ForumBackTopButton from '../../components/ForumBackTopButton.vue'
import RoleTag from '../../components/RoleTag.vue'
import { useAuthStore } from '../../stores/auth'
import { useForumStore } from '../../stores/forum'
import { getFirstSentence } from '../../utils/content'

const router = useRouter()
const store = useForumStore()
const auth = useAuthStore()
const sort = ref<'latest' | 'hot'>('latest')

const categories = computed(() => store.categories)
const posts = computed(() => store.posts)
const sortOptions = [
  { label: '最新', value: 'latest' },
  { label: '最热', value: 'hot' },
]

async function loadPosts() {
  await store.loadPosts(sort.value)
}

function postTypeLabel(type: string) {
  const map: Record<string, string> = {
    general: '普通帖',
    contest: '竞赛资讯',
    recruit_project: '项目招募',
    recruit_team: '组队招募',
    notice: '公告帖',
  }
  return map[type] || '帖子'
}

onMounted(async () => {
  await Promise.all([store.loadCategories(), loadPosts()])
})
</script>

<style scoped>
.forum-home {
  display: grid;
  gap: 16px;
}

.forum-home__hero {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.18), transparent 26%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(241, 245, 249, 0.95));
}

.forum-home__hero-top,
.forum-home__hero-actions,
.forum-home__posts-head,
.forum-home__post-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.forum-home__hero-copy {
  max-width: 760px;
}

.forum-home__eyebrow {
  display: inline-flex;
  min-height: 32px;
  align-items: center;
  padding: 0 12px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.forum-home h1 {
  margin: 16px 0 10px;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.1;
}

.forum-home p,
.forum-home__posts-subtitle,
.forum-home__post-excerpt {
  margin: 0;
  color: #64748b;
  line-height: 1.75;
}

.forum-home__hero-actions {
  flex-direction: column;
  min-width: 150px;
}

.forum-home__hero-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.forum-home__hero-stat {
  padding: 16px 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.forum-home__hero-stat span,
.forum-home__hero-stat small {
  display: block;
  color: #64748b;
}

.forum-home__hero-stat strong {
  display: block;
  margin: 8px 0;
  font-size: 32px;
  color: #0f172a;
}

.forum-home__boards-card {
  padding: 0;
}

.forum-home__board-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.forum-home__board-pill {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-height: 44px;
  padding: 0 14px;
  border-radius: 16px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid rgba(148, 163, 184, 0.14);
  transition: all 0.2s ease;
}

.forum-home__board-pill:hover {
  transform: translateY(-1px);
  border-color: rgba(59, 130, 246, 0.26);
  box-shadow: 0 12px 24px rgba(15, 23, 42, 0.06);
}

.forum-home__board-name {
  color: #0f172a;
  font-size: 14px;
  font-weight: 700;
}

.forum-home__board-count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 8px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 800;
}

.forum-home__post-list {
  display: grid;
  gap: 14px;
}

.forum-home__post-card {
  display: block;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid rgba(148, 163, 184, 0.16);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.forum-home__post-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.26);
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.08);
}

.forum-home__post-badges,
.forum-home__post-bottom {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.forum-home__post-type,
.forum-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.forum-home__post-type {
  background: #f1f5f9;
  color: #475569;
}

.forum-pill--top {
  background: #dbeafe;
  color: #2563eb;
}

.forum-pill--essence {
  background: #fef3c7;
  color: #b45309;
}

.forum-home__posts-title {
  font-size: 24px;
  color: #0f172a;
}

.forum-home__post-card h3 {
  margin: 14px 0 10px;
  font-size: 22px;
  color: #0f172a;
}

.forum-home__post-bottom {
  margin-top: 14px;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 960px) {
  .forum-home__hero-top,
  .forum-home__hero-actions,
  .forum-home__posts-head,
  .forum-home__post-top {
    flex-direction: column;
    align-items: stretch;
  }

  .forum-home__hero-actions {
    width: 100%;
    min-width: 0;
  }

  .forum-home__hero-actions :deep(.el-button) {
    width: 100%;
  }

  .forum-home__hero-stats {
    grid-template-columns: 1fr;
  }
}
</style>