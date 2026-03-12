<template>
  <div class="card-grid">
    <el-card v-if="post">
      <template #header>
        <div class="section-title">
          <div>
            <span>{{ post.title }}</span>
            <RoleTag :user="post.author" />
          </div>
          <div>
            <el-button @click="likePost">点赞 {{ post.likes_count }}</el-button>
          </div>
        </div>
      </template>
      <MarkdownContent :content="post.content" />
    </el-card>

    <el-card>
      <template #header>
        <div class="section-title"><span>评论</span></div>
      </template>
      <el-empty v-if="!comments.length" description="还没有评论" />
      <el-space v-else direction="vertical" fill>
        <el-card v-for="comment in comments" :key="comment.id" shadow="never">
          <div class="section-title">
            <span>{{ comment.author.username }}</span>
            <RoleTag :user="comment.author" />
          </div>
          <MarkdownContent :content="comment.content" />
        </el-card>
      </el-space>
      <el-form v-if="auth.isAuthenticated" class="comment-form" @submit.prevent="submitComment">
        <el-form-item>
          <el-input v-model="commentContent" type="textarea" :rows="4" placeholder="输入评论内容" />
        </el-form-item>
        <el-button type="primary" @click="submitComment">发表评论</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute } from 'vue-router'

import MarkdownContent from '../../components/MarkdownContent.vue'
import RoleTag from '../../components/RoleTag.vue'
import { useAuthStore } from '../../stores/auth'
import { useForumStore } from '../../stores/forum'

const route = useRoute()
const forum = useForumStore()
const auth = useAuthStore()
const commentContent = ref('')

const post = computed(() => forum.currentPost)
const comments = computed(() => forum.comments)

async function loadPost() {
  await forum.loadPost(Number(route.params.id))
}

async function submitComment() {
  if (!commentContent.value.trim() || !post.value) return
  await forum.submitComment(post.value.id, { content: commentContent.value })
  commentContent.value = ''
  ElMessage.success('评论已发布')
}

async function likePost() {
  if (!post.value) return
  await forum.likePost(post.value.id)
}

onMounted(loadPost)
</script>

<style scoped>
.comment-form {
  margin-top: 16px;
}
</style>
