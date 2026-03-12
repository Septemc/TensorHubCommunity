<template>
  <div class="card-grid two">
    <el-card>
      <template #header>
        <div class="section-title"><span>论坛板块</span></div>
      </template>
      <el-empty v-if="!categories.length" description="暂无板块" />
      <el-space v-else direction="vertical" fill>
        <el-card v-for="item in categories" :key="item.id" shadow="never">
          <RouterLink :to="`/forum/category/${item.id}`">{{ item.name }}</RouterLink>
          <p>{{ item.description }}</p>
        </el-card>
      </el-space>
    </el-card>

    <el-card>
      <template #header>
        <div class="section-title">
          <span>最新帖子</span>
          <el-radio-group v-model="sort" size="small" @change="loadPosts">
            <el-radio-button label="latest">最新</el-radio-button>
            <el-radio-button label="hot">最热</el-radio-button>
          </el-radio-group>
        </div>
      </template>
      <el-empty v-if="!posts.length" description="暂无帖子" />
      <el-space v-else direction="vertical" fill>
        <el-card v-for="item in posts" :key="item.id" shadow="never">
          <div class="section-title">
            <RouterLink :to="`/forum/post/${item.id}`">{{ item.title }}</RouterLink>
            <RoleTag :user="item.author" />
          </div>
          <small>点赞 {{ item.likes_count }} · 评论 {{ item.comments_count }} · 浏览 {{ item.views }}</small>
        </el-card>
      </el-space>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

import RoleTag from '../../components/RoleTag.vue'
import { useForumStore } from '../../stores/forum'

const store = useForumStore()
const sort = ref('latest')
const categories = computed(() => store.categories)
const posts = computed(() => store.posts)

async function loadPosts() {
  await store.loadPosts(sort.value)
}

onMounted(async () => {
  await Promise.all([store.loadCategories(), loadPosts()])
})
</script>
