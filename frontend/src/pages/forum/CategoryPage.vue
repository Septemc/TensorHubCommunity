<template>
  <div class="forum-category">
    <el-card class="forum-category__hero">
      <div class="forum-category__hero-top">
        <div>
          <div class="forum-category__eyebrow">Category</div>
          <h1>{{ category?.name || '板块详情' }}</h1>
          <p>{{ category?.description || '浏览这个板块下的全部讨论内容。' }}</p>
        </div>
        <div class="forum-category__actions">
          <el-segmented v-model="sort" :options="sortOptions" @change="loadPosts" />
          <el-button type="primary" @click="router.push(auth.isVerified ? '/forum/create' : '/login')">
            {{ auth.isVerified ? '发布帖子' : '登录后发帖' }}
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <div class="section-title forum-category__list-header">
          <div>
            <span class="forum-category__list-title">板块帖子</span>
            <p class="forum-category__list-subtitle">{{ posts.length }} 条可见内容</p>
          </div>
        </div>
      </template>

      <el-empty v-if="!posts.length" description="暂无帖子" />
      <div v-else class="forum-category__post-list">
        <RouterLink v-for="item in posts" :key="item.id" :to="`/forum/post/${item.id}`" class="forum-category__post-card">
          <div class="forum-category__post-top">
            <div class="forum-category__post-badges">
              <span v-if="item.is_top" class="forum-pill forum-pill--top">置顶</span>
              <span v-if="item.is_essence" class="forum-pill forum-pill--essence">精华</span>
              <span class="forum-category__post-type">{{ postTypeLabel(item.post_type) }}</span>
            </div>
            <RoleTag :user="item.author" />
          </div>
          <h3>{{ item.title }}</h3>
          <p class="forum-category__post-excerpt">{{ getFirstSentence(item.content) }}</p>
          <div class="forum-category__post-bottom">
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
import { useRoute, useRouter } from 'vue-router'

import ForumBackTopButton from '../../components/ForumBackTopButton.vue'
import RoleTag from '../../components/RoleTag.vue'
import { useAuthStore } from '../../stores/auth'
import { useForumStore } from '../../stores/forum'
import { getFirstSentence } from '../../utils/content'

const route = useRoute()
const router = useRouter()
const store = useForumStore()
const auth = useAuthStore()
const sort = ref<'latest' | 'hot'>('latest')

const categoryId = computed(() => Number(route.params.id))
const posts = computed(() => store.posts)
const category = computed(() => store.categories.find((item) => item.id === categoryId.value))
const sortOptions = [
  { label: '最新', value: 'latest' },
  { label: '最热', value: 'hot' },
]

async function loadPosts() {
  await store.loadCategoryPosts(categoryId.value, sort.value)
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
  await store.loadCategories()
  await loadPosts()
})
</script>

<style scoped>
.forum-category {
  display: grid;
  gap: 20px;
}

.forum-category__hero {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.18), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.95));
}

.forum-category__hero-top,
.forum-category__actions,
.forum-category__post-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.forum-category__eyebrow {
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

.forum-category__hero h1 {
  margin: 16px 0 12px;
  font-size: clamp(26px, 4vw, 38px);
  line-height: 1.1;
}

.forum-category__hero p,
.forum-category__list-subtitle,
.forum-category__post-excerpt {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.forum-category__actions {
  flex-direction: column;
  min-width: 170px;
}

.forum-category__list-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.forum-category__post-list {
  display: grid;
  gap: 14px;
}

.forum-category__post-card {
  display: block;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid rgba(148, 163, 184, 0.16);
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.forum-category__post-card:hover {
  transform: translateY(-2px);
  border-color: rgba(59, 130, 246, 0.26);
  box-shadow: 0 18px 30px rgba(15, 23, 42, 0.08);
}

.forum-category__post-badges,
.forum-category__post-bottom {
  display: flex;
  flex-wrap: wrap;
  gap: 8px 12px;
}

.forum-category__post-type,
.forum-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.forum-category__post-type {
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

.forum-category__post-card h3 {
  margin: 16px 0 12px;
  font-size: 22px;
  color: #0f172a;
}

.forum-category__post-bottom {
  margin-top: 16px;
  color: #64748b;
  font-size: 13px;
}

@media (max-width: 960px) {
  .forum-category__hero-top,
  .forum-category__actions,
  .forum-category__post-top {
    flex-direction: column;
    align-items: flex-start;
  }

  .forum-category__actions {
    width: 100%;
    min-width: 0;
  }

  .forum-category__actions :deep(.el-button) {
    width: 100%;
  }
}
</style>