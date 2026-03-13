<template>
  <div class="user-settings-page">
    <div class="card-grid two user-settings-page__top">
      <el-card>
        <template #header>
          <div class="section-title"><span>个人资料</span></div>
        </template>

        <div v-if="auth.user" class="profile-summary">
          <div class="profile-summary__top">
            <el-avatar :size="72" :src="auth.user.avatar || undefined">
              {{ auth.user.username.slice(0, 1).toUpperCase() }}
            </el-avatar>
            <div>
              <h2>{{ auth.user.real_name || auth.user.username }}</h2>
              <p>@{{ auth.user.username }}</p>
              <el-tag :type="statusTagType">{{ statusLabel }}</el-tag>
            </div>
          </div>

          <div class="profile-summary__grid">
            <div><strong>邮箱</strong><span>{{ auth.user.email || '未填写' }}</span></div>
            <div><strong>专业</strong><span>{{ auth.user.major || '未填写' }}</span></div>
            <div><strong>学号</strong><span>{{ auth.user.student_id || '未填写' }}</span></div>
            <div><strong>性别</strong><span>{{ auth.user.gender || '未填写' }}</span></div>
          </div>

          <el-alert
            v-if="auth.user.verification_status !== 'approved'"
            title="当前账号尚未审核通过，暂时不能发帖。"
            type="warning"
            :closable="false"
            show-icon
          />
        </div>
      </el-card>

      <el-card>
        <template #header>
          <div class="section-title"><span>更新资料</span></div>
        </template>

        <el-form label-position="top" :model="form" class="profile-form">
          <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
          <el-form-item label="专业"><el-input v-model="form.major" /></el-form-item>
          <el-form-item label="性别"><el-input v-model="form.gender" /></el-form-item>
          <el-form-item label="真实姓名"><el-input v-model="form.real_name" /></el-form-item>
          <el-form-item label="头像上传">
            <input type="file" accept="image/*" @change="onFileChange" />
          </el-form-item>
          <el-button type="primary" :loading="savingProfile" @click="submitProfile">保存资料</el-button>
        </el-form>
      </el-card>
    </div>

    <el-card>
      <template #header>
        <div class="section-title user-settings-page__posts-header">
          <div>
            <span>我的帖子</span>
            <p>{{ myPosts.length }} 篇内容，可直接修改或删除</p>
          </div>
          <el-button type="primary" plain @click="router.push('/forum/create')">新建帖子</el-button>
        </div>
      </template>

      <el-empty v-if="!myPosts.length" description="你还没有发布帖子" />
      <div v-else class="user-post-list">
        <div v-for="post in myPosts" :key="post.id" class="user-post-card">
          <div class="user-post-card__head">
            <div>
              <RouterLink :to="`/forum/post/${post.id}`" class="user-post-card__title">{{ post.title }}</RouterLink>
              <div class="user-post-card__meta">
                <span>点赞 {{ post.likes_count }}</span>
                <span>评论 {{ post.comments_count }}</span>
                <span>浏览 {{ post.views }}</span>
                <span>{{ formatDate(post.updated_at || post.created_at) }}</span>
              </div>
            </div>
            <div class="user-post-card__actions">
              <el-button plain @click="router.push(`/forum/post/${post.id}/edit`)">编辑</el-button>
              <el-button type="danger" plain :loading="deletingId === post.id" @click="openDelete(post.id)">删除</el-button>
            </div>
          </div>
          <p class="user-post-card__excerpt">{{ getFirstSentence(post.content) }}</p>
        </div>
      </div>
    </el-card>

    <ForumConfirmDialog
      v-model="deleteVisible"
      title="删除帖子"
      message="删除后不可恢复，确认继续吗？"
      confirm-text="确认删除"
      @confirm="removePost"
    />
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, reactive, ref, watchEffect } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { uploadImage } from '../../api/admin'
import ForumConfirmDialog from '../../components/ForumConfirmDialog.vue'
import { useAuthStore } from '../../stores/auth'
import { useForumStore } from '../../stores/forum'
import { getFirstSentence } from '../../utils/content'

const auth = useAuthStore()
const forum = useForumStore()
const router = useRouter()

const form = reactive({
  email: '',
  major: '',
  gender: '',
  real_name: '',
  avatar: '',
})

const savingProfile = ref(false)
const deletingId = ref<number | null>(null)
const pendingDeleteId = ref<number | null>(null)
const deleteVisible = ref(false)
const myPosts = computed(() => forum.userPosts)
const statusLabel = computed(() => {
  const map = {
    pending: '待审核',
    approved: '已审核通过',
    rejected: '已驳回',
  }
  return map[auth.user?.verification_status || 'pending']
})
const statusTagType = computed(() => {
  if (auth.user?.verification_status === 'approved') return 'success'
  if (auth.user?.verification_status === 'rejected') return 'danger'
  return 'warning'
})

watchEffect(() => {
  form.email = auth.user?.email || ''
  form.major = auth.user?.major || ''
  form.gender = auth.user?.gender || ''
  form.real_name = auth.user?.real_name || ''
  form.avatar = auth.user?.avatar || ''
})

async function loadMyPosts() {
  if (auth.user) {
    await forum.loadUserPosts(auth.user.id)
  }
}

async function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const result = await uploadImage(file)
  form.avatar = result.url
}

async function submitProfile() {
  try {
    savingProfile.value = true
    await auth.saveProfile(form)
    ElMessage.success('资料已更新')
  } finally {
    savingProfile.value = false
  }
}

function openDelete(postId: number) {
  pendingDeleteId.value = postId
  deleteVisible.value = true
}

async function removePost() {
  if (!pendingDeleteId.value) return
  try {
    deletingId.value = pendingDeleteId.value
    await forum.removePost(pendingDeleteId.value)
    ElMessage.success('帖子已删除')
  } catch (error) {
    const message = axios.isAxiosError(error)
      ? (error.response?.data?.detail ?? '删除失败')
      : '删除失败'
    ElMessage.error(message)
  } finally {
    deletingId.value = null
    pendingDeleteId.value = null
  }
}

function formatDate(value?: string | null) {
  if (!value) return '刚刚'
  return new Date(value).toLocaleString('zh-CN', { hour12: false })
}

onMounted(loadMyPosts)
</script>

<style scoped>
.user-settings-page {
  display: grid;
  gap: 20px;
}

.profile-summary {
  display: grid;
  gap: 20px;
}

.profile-summary__top,
.user-settings-page__posts-header,
.user-post-card__head,
.user-post-card__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.profile-summary__top h2 {
  margin: 0 0 8px;
  font-size: 28px;
}

.profile-summary__top p {
  margin: 0 0 10px;
  color: #64748b;
}

.profile-summary__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.profile-summary__grid div,
.user-post-card {
  padding: 16px 18px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.profile-summary__grid strong {
  display: block;
  margin-bottom: 8px;
  color: #0f172a;
}

.profile-summary__grid span,
.user-post-card__meta,
.user-post-card__excerpt,
.user-settings-page__posts-header p {
  color: #64748b;
}

.profile-form {
  display: grid;
  gap: 4px;
}

.user-post-list {
  display: grid;
  gap: 14px;
}

.user-post-card__title {
  font-size: 20px;
  font-weight: 800;
  color: #0f172a;
}

.user-post-card__meta {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  font-size: 13px;
}

.user-post-card__excerpt {
  margin: 14px 0 0;
  line-height: 1.7;
}

@media (max-width: 960px) {
  .profile-summary__top,
  .user-settings-page__posts-header,
  .user-post-card__head,
  .user-post-card__actions {
    flex-direction: column;
    align-items: flex-start;
  }

  .profile-summary__grid {
    grid-template-columns: 1fr;
  }
}
</style>