<template>
  <div class="post-detail">
    <el-card v-if="post" class="post-detail__hero">
      <div class="post-detail__hero-top">
        <div class="post-detail__badges">
          <span v-if="post.is_top" class="forum-pill forum-pill--top">置顶</span>
          <span v-if="post.is_essence" class="forum-pill forum-pill--essence">精华</span>
          <span class="post-detail__type">{{ postTypeLabel(post.post_type) }}</span>
        </div>
        <div class="post-detail__toolbar">
          <el-button plain @click="router.push('/forum')">返回论坛</el-button>
          <div v-if="canManagePost" class="post-detail__menu-wrap">
            <button type="button" class="post-detail__menu-trigger" @click="menuOpen = !menuOpen">⋯</button>
            <div v-if="menuOpen" class="post-detail__menu-panel">
              <button type="button" @click="goEdit">编辑</button>
              <button type="button" class="is-danger" @click="openDeleteConfirm">删除</button>
            </div>
          </div>
        </div>
      </div>

      <div class="post-detail__title-row">
        <div>
          <h1>{{ post.title }}</h1>
          <div class="post-detail__meta">
            <span>作者 {{ post.author.username }}</span>
            <span>浏览 {{ post.views }}</span>
            <span>评论 {{ post.comments_count }}</span>
            <span>{{ formatDate(post.created_at) }}</span>
          </div>
        </div>
        <RoleTag :user="post.author" />
      </div>

      <div v-if="post.extra_data && Object.keys(post.extra_data).length" class="post-detail__extra">
        <div class="post-detail__extra-title">附加信息</div>
        <pre>{{ JSON.stringify(post.extra_data, null, 2) }}</pre>
      </div>

      <div class="post-detail__content">
        <MarkdownContent :content="post.content" />
      </div>

      <div class="post-detail__content-footer">
        <el-button type="primary" plain @click="likePost">点赞 {{ post.likes_count }}</el-button>
      </div>
    </el-card>

    <el-card class="post-detail__comments">
      <template #header>
        <div class="section-title post-detail__comment-header">
          <div>
            <span class="post-detail__comment-title">评论区</span>
            <p class="post-detail__comment-subtitle">{{ comments.length }} 条互动内容</p>
          </div>
          <div class="post-detail__comment-tools">
            <span v-if="replyTarget">正在回复 {{ replyTarget.author.username }}</span>
            <el-button v-if="replyTarget" text @click="clearReply">取消回复</el-button>
          </div>
        </div>
      </template>

      <el-empty v-if="!comments.length" description="还没有评论，来抢个沙发吧" />
      <div v-else class="post-detail__comment-list">
        <div v-for="comment in comments" :key="comment.id" class="post-comment-card">
          <div class="post-comment-card__header">
            <div>
              <strong>{{ comment.author.username }}</strong>
              <div class="post-comment-card__meta">
                <span>{{ formatDate(comment.created_at) }}</span>
                <span>点赞 {{ comment.likes_count }}</span>
                <span v-if="comment.parent_id">回复评论 #{{ comment.parent_id }}</span>
              </div>
            </div>
            <div class="post-comment-card__header-actions">
              <RoleTag :user="comment.author" />
              <el-button v-if="auth.isAuthenticated" text @click="setReply(comment)">回复</el-button>
            </div>
          </div>
          <div class="post-comment-card__content">
            <MarkdownContent :content="comment.content" />
          </div>
        </div>
      </div>

      <el-form v-if="auth.isAuthenticated" class="post-detail__comment-form" @submit.prevent="submitComment">
        <el-form-item>
          <el-input
            v-model="commentContent"
            type="textarea"
            :rows="5"
            maxlength="1000"
            show-word-limit
            placeholder="输入你的评论内容，友好交流更受欢迎。"
          />
        </el-form-item>
        <div class="post-detail__comment-actions">
          <span class="post-detail__comment-tip">
            {{ replyTarget ? `将作为对 ${replyTarget.author.username} 的回复发布` : '支持 Markdown，建议用短段落和列表提升可读性' }}
          </span>
          <el-button type="primary" :loading="submittingComment" @click="submitComment">发表评论</el-button>
        </div>
      </el-form>
      <el-empty v-else description="登录后参与讨论" />
    </el-card>

    <ForumConfirmDialog
      v-model="deleteConfirmVisible"
      title="删除帖子"
      message="删除后帖子无法恢复，评论内容也将不再显示。确认继续吗？"
      confirm-text="确认删除"
      @confirm="confirmDelete"
    />
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import ForumConfirmDialog from '../../components/ForumConfirmDialog.vue'
import MarkdownContent from '../../components/MarkdownContent.vue'
import RoleTag from '../../components/RoleTag.vue'
import { useAuthStore } from '../../stores/auth'
import { useForumStore } from '../../stores/forum'
import type { Comment } from '../../types/models'

const route = useRoute()
const router = useRouter()
const forum = useForumStore()
const auth = useAuthStore()

const commentContent = ref('')
const replyTarget = ref<Comment | null>(null)
const deleting = ref(false)
const submittingComment = ref(false)
const menuOpen = ref(false)
const deleteConfirmVisible = ref(false)

const post = computed(() => forum.currentPost)
const comments = computed(() => forum.comments)
const canManagePost = computed(() => {
  if (!post.value || !auth.user) return false
  return auth.user.id === post.value.user_id || auth.isAdmin
})

async function loadPost() {
  await forum.loadPost(Number(route.params.id))
  commentContent.value = ''
  replyTarget.value = null
  menuOpen.value = false
}

function setReply(comment: Comment) {
  replyTarget.value = comment
}

function clearReply() {
  replyTarget.value = null
}

function goEdit() {
  if (!post.value) return
  menuOpen.value = false
  router.push(`/forum/post/${post.value.id}/edit`)
}

function openDeleteConfirm() {
  menuOpen.value = false
  deleteConfirmVisible.value = true
}

async function confirmDelete() {
  if (!post.value) return
  try {
    deleting.value = true
    await forum.removePost(post.value.id)
    ElMessage.success('帖子已删除')
    router.push('/forum')
  } catch (error) {
    const message = axios.isAxiosError(error)
      ? (error.response?.data?.detail ?? '删除失败')
      : '删除失败'
    ElMessage.error(message)
  } finally {
    deleting.value = false
  }
}

async function submitComment() {
  if (!commentContent.value.trim() || !post.value) return
  try {
    submittingComment.value = true
    await forum.submitComment(post.value.id, { content: commentContent.value.trim(), parent_id: replyTarget.value?.id })
    commentContent.value = ''
    replyTarget.value = null
    ElMessage.success('评论已发布')
  } catch (error) {
    const message = axios.isAxiosError(error)
      ? (error.response?.data?.detail ?? '评论发布失败')
      : '评论发布失败'
    ElMessage.error(message)
  } finally {
    submittingComment.value = false
  }
}

async function likePost() {
  if (!post.value) return
  await forum.likePost(post.value.id)
  ElMessage.success('已更新点赞状态')
}

function formatDate(value?: string | null) {
  if (!value) return '刚刚'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
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

watch(() => route.params.id, loadPost)
onMounted(loadPost)
</script>

<style scoped>
.post-detail {
  display: grid;
  gap: 20px;
}

.post-detail__hero {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.16), transparent 26%),
    linear-gradient(180deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.94));
}

.post-detail__hero-top,
.post-detail__title-row,
.post-comment-card__header,
.post-detail__comment-actions,
.post-detail__comment-header,
.post-detail__toolbar,
.post-detail__content-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.post-detail__badges,
.post-comment-card__header-actions,
.post-detail__comment-tools {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.post-detail__type,
.forum-pill {
  display: inline-flex;
  align-items: center;
  min-height: 28px;
  padding: 0 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 700;
}

.post-detail__type {
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

.post-detail__menu-wrap {
  position: relative;
}

.post-detail__menu-trigger {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.18);
  background: #fff;
  font-size: 24px;
  line-height: 1;
  cursor: pointer;
}

.post-detail__menu-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 132px;
  padding: 8px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.98);
  border: 1px solid rgba(148, 163, 184, 0.18);
  box-shadow: 0 18px 40px rgba(15, 23, 42, 0.12);
}

.post-detail__menu-panel button {
  width: 100%;
  min-height: 40px;
  border: none;
  background: transparent;
  text-align: left;
  border-radius: 12px;
  padding: 0 12px;
  color: #0f172a;
  cursor: pointer;
}

.post-detail__menu-panel button:hover {
  background: #f8fafc;
}

.post-detail__menu-panel button.is-danger {
  color: #dc2626;
}

.post-detail__title-row {
  margin-top: 20px;
  align-items: flex-start;
}

.post-detail__title-row h1 {
  margin: 0;
  font-size: clamp(28px, 4vw, 42px);
  line-height: 1.15;
}

.post-detail__meta {
  margin-top: 14px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #64748b;
  font-size: 14px;
}

.post-detail__extra {
  margin-top: 20px;
  padding: 18px;
  border-radius: 18px;
  background: rgba(248, 250, 252, 0.88);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.post-detail__extra-title {
  margin-bottom: 10px;
  font-weight: 800;
  color: #0f172a;
}

.post-detail__extra pre {
  margin: 0;
  white-space: pre-wrap;
  color: #475569;
}

.post-detail__content {
  margin-top: 22px;
  padding-top: 22px;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
}

.post-detail__content-footer {
  margin-top: 22px;
  padding-top: 18px;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
  justify-content: flex-end;
}

.post-detail__comment-title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.post-detail__comment-subtitle,
.post-detail__comment-tip {
  margin: 8px 0 0;
  color: #64748b;
  font-size: 14px;
}

.post-detail__comment-list {
  display: grid;
  gap: 14px;
}

.post-comment-card {
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.post-comment-card__meta {
  margin-top: 6px;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  color: #64748b;
  font-size: 13px;
}

.post-comment-card__content {
  margin-top: 14px;
}

.post-detail__comment-form {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid rgba(148, 163, 184, 0.18);
}

@media (max-width: 960px) {
  .post-detail__hero-top,
  .post-detail__title-row,
  .post-comment-card__header,
  .post-detail__comment-actions,
  .post-detail__comment-header,
  .post-detail__toolbar,
  .post-detail__content-footer {
    flex-direction: column;
    align-items: stretch;
  }

  .post-detail__toolbar :deep(.el-button),
  .post-detail__content-footer :deep(.el-button) {
    width: 100%;
  }
}
</style>