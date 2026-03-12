<template>
  <el-card>
    <template #header>
      <div class="section-title">
        <span>{{ category?.name || '板块详情' }}</span>
        <el-radio-group v-model="sort" size="small" @change="loadPosts">
          <el-radio-button label="latest">最新</el-radio-button>
          <el-radio-button label="hot">最热</el-radio-button>
        </el-radio-group>
      </div>
    </template>
    <el-empty v-if="!posts.length" description="暂无帖子" />
    <el-space v-else direction="vertical" fill>
      <el-card v-for="item in posts" :key="item.id" shadow="never">
        <RouterLink :to="`/forum/post/${item.id}`">{{ item.title }}</RouterLink>
      </el-card>
    </el-space>
  </el-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { useForumStore } from '../../stores/forum'

const route = useRoute()
const store = useForumStore()
const sort = ref('latest')

const categoryId = computed(() => Number(route.params.id))
const posts = computed(() => store.posts)
const category = computed(() => store.categories.find((item) => item.id === categoryId.value))

async function loadPosts() {
  await store.loadCategoryPosts(categoryId.value, sort.value)
}

onMounted(async () => {
  await store.loadCategories()
  await loadPosts()
})
</script>
