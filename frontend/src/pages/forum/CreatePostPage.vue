<template>
  <div class="create-post-page">
    <el-card class="create-post-page__hero">
      <div class="create-post-page__hero-content">
        <div>
          <div class="create-post-page__eyebrow">{{ isEditMode ? 'Edit Post' : 'Create Post' }}</div>
          <h1>{{ isEditMode ? '编辑帖子' : '发布帖子' }}</h1>
          <p>
            {{
              isEditMode
                ? '调整标题、板块和正文内容，保存后会立即同步到帖子页。'
                : '选择板块、组织标题与正文，快速把你的经验、资讯或招募需求发布到社区。'
            }}
          </p>
        </div>
        <div class="create-post-page__hero-actions">
          <el-button plain @click="router.push('/forum')">返回论坛</el-button>
          <el-button v-if="isEditMode && currentPost" type="danger" plain :loading="deleting" @click="deleteVisible = true">
            删除帖子
          </el-button>
        </div>
      </div>
    </el-card>

    <el-card>
      <template #header>
        <div class="section-title create-post-page__header">
          <div>
            <span class="create-post-page__title">帖子内容</span>
            <p class="create-post-page__subtitle">支持 Markdown、实时预览和结构化附加信息。</p>
          </div>
          <div class="create-post-page__header-meta">
            <span>标题 {{ form.title.trim().length }}/60</span>
            <span>正文 {{ form.content.trim().length }} 字</span>
          </div>
        </div>
      </template>

      <el-alert
        v-if="auth.user?.verification_status !== 'approved'"
        title="当前账号尚未审核通过，暂时不能发帖。"
        type="warning"
        show-icon
        :closable="false"
      />

      <el-form label-position="top" :model="form" class="create-post-page__form">
        <div class="card-grid two">
          <el-form-item label="板块">
            <el-select v-model="form.category_id" style="width: 100%" placeholder="请选择板块">
              <el-option v-for="item in forum.categories" :key="item.id" :label="item.name" :value="item.id" />
            </el-select>
          </el-form-item>

          <el-form-item label="帖子类型">
            <el-select v-model="form.post_type" style="width: 100%">
              <el-option label="普通帖" value="general" />
              <el-option label="竞赛资讯" value="contest" />
              <el-option label="项目招募" value="recruit_project" />
              <el-option label="组队招募" value="recruit_team" />
            </el-select>
          </el-form-item>
        </div>

        <el-form-item label="标题">
          <el-input v-model="form.title" maxlength="60" show-word-limit placeholder="用一句清晰的话概括你的主题" />
        </el-form-item>

        <div class="card-grid two create-post-page__editor-grid">
          <div>
            <el-form-item label="正文 Markdown">
              <el-input
                v-model="form.content"
                type="textarea"
                :rows="16"
                resize="vertical"
                placeholder="建议按背景、过程、结果或招募要求组织内容。"
              />
            </el-form-item>

            <el-form-item label="结构化附加信息（JSON，可选）">
              <el-input
                v-model="extraDataText"
                type="textarea"
                :rows="6"
                resize="vertical"
                placeholder='例如：{"deadline":"2026-04-01","skills":["Vue","FastAPI"]}'
              />
            </el-form-item>
          </div>

          <div class="create-post-page__preview">
            <div class="create-post-page__preview-head">
              <span>实时预览</span>
              <span>{{ postTypeLabel }}</span>
            </div>
            <div class="create-post-page__preview-body">
              <h3>{{ form.title || '标题预览' }}</h3>
              <MarkdownContent :content="form.content || '正文预览会显示在这里。'" />
            </div>
          </div>
        </div>

        <div class="create-post-page__tips">
          <div class="create-post-page__tip"><strong>建议结构</strong><span>背景 → 关键内容 → 结果 / 招募要求</span></div>
          <div class="create-post-page__tip"><strong>可读性</strong><span>多用小标题、列表和代码块，减少长段落堆叠。</span></div>
          <div class="create-post-page__tip"><strong>说明完整</strong><span>招募帖建议写清方向、技能、截止时间和联系方式。</span></div>
        </div>

        <div class="create-post-page__actions">
          <el-button type="primary" size="large" :loading="submitting" :disabled="!auth.isVerified" @click="submit">
            {{ isEditMode ? '保存修改' : '提交帖子' }}
          </el-button>
          <el-button size="large" @click="router.push(isEditMode && currentPost ? `/forum/post/${currentPost.id}` : '/forum')">
            取消
          </el-button>
        </div>
      </el-form>
    </el-card>

    <ForumConfirmDialog
      v-model="deleteVisible"
      title="删除帖子"
      message="删除后帖子和关联内容不可恢复，确认继续吗？"
      confirm-text="确认删除"
      @confirm="remove"
    />
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useRoute, useRouter } from 'vue-router'

import ForumConfirmDialog from '../../components/ForumConfirmDialog.vue'
import MarkdownContent from '../../components/MarkdownContent.vue'
import { useAuthStore } from '../../stores/auth'
import { useForumStore } from '../../stores/forum'

const auth = useAuthStore()
const forum = useForumStore()
const router = useRouter()
const route = useRoute()

const submitting = ref(false)
const deleting = ref(false)
const deleteVisible = ref(false)
const extraDataText = ref('')

const form = reactive({
  title: '',
  content: '',
  category_id: undefined as number | undefined,
  post_type: 'general',
})

const isEditMode = computed(() => Boolean(route.params.id))
const currentPost = computed(() => forum.currentPost)
const postTypeLabel = computed(() => {
  const map: Record<string, string> = {
    general: '普通帖',
    contest: '竞赛资讯',
    recruit_project: '项目招募',
    recruit_team: '组队招募',
  }
  return map[form.post_type] || '帖子'
})

async function initPage() {
  await forum.loadCategories()
  if (!isEditMode.value) {
    form.title = ''
    form.content = ''
    form.category_id = forum.categories[0]?.id
    form.post_type = 'general'
    extraDataText.value = ''
    return
  }

  const post = await forum.loadPost(Number(route.params.id))
  if (!post) {
    router.push('/forum')
    return
  }
  const canEdit = auth.user && (auth.user.id === post.user_id || auth.isAdmin)
  if (!canEdit) {
    ElMessage.error('你没有权限编辑这篇帖子')
    router.push(`/forum/post/${post.id}`)
    return
  }

  form.title = post.title
  form.content = post.content
  form.category_id = post.category_id
  form.post_type = post.post_type
  extraDataText.value = post.extra_data ? JSON.stringify(post.extra_data, null, 2) : ''
}

function buildPayload() {
  if (!form.category_id) {
    throw new Error('请选择板块')
  }
  if (form.title.trim().length < 3) {
    throw new Error('标题至少需要 3 个字符')
  }
  if (form.content.trim().length < 10) {
    throw new Error('正文至少需要 10 个字符')
  }

  let extraData = undefined
  if (extraDataText.value.trim()) {
    try {
      extraData = JSON.parse(extraDataText.value)
    } catch {
      throw new Error('附加信息必须是合法 JSON')
    }
  }

  return {
    title: form.title.trim(),
    content: form.content.trim(),
    category_id: form.category_id,
    post_type: form.post_type,
    extra_data: extraData,
  }
}

async function submit() {
  try {
    submitting.value = true
    const payload = buildPayload()
    if (isEditMode.value && currentPost.value) {
      const post = await forum.savePost(currentPost.value.id, payload)
      ElMessage.success('帖子已更新')
      router.push(`/forum/post/${post.id}`)
      return
    }
    const post = await forum.submitPost(payload)
    ElMessage.success('帖子发布成功')
    router.push(`/forum/post/${post.id}`)
  } catch (error) {
    const message = error instanceof Error
      ? error.message
      : axios.isAxiosError(error)
        ? (error.response?.data?.detail ?? '提交失败，请检查后端状态')
        : '提交失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    submitting.value = false
  }
}

async function remove() {
  if (!currentPost.value) return
  try {
    deleting.value = true
    await forum.removePost(currentPost.value.id)
    ElMessage.success('帖子已删除')
    router.push('/forum')
  } catch (error) {
    const message = axios.isAxiosError(error)
      ? (error.response?.data?.detail ?? '删除失败，请稍后重试')
      : '删除失败，请稍后重试'
    ElMessage.error(message)
  } finally {
    deleting.value = false
  }
}

watch(() => route.params.id, initPage)
onMounted(initPage)
</script>

<style scoped>
.create-post-page {
  display: grid;
  gap: 20px;
}

.create-post-page__hero {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.16), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(248, 250, 252, 0.95));
}

.create-post-page__hero-content,
.create-post-page__hero-actions,
.create-post-page__actions,
.create-post-page__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 24px;
}

.create-post-page__eyebrow {
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

.create-post-page__hero h1 {
  margin: 16px 0 12px;
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.1;
}

.create-post-page__hero p,
.create-post-page__subtitle {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.create-post-page__hero-actions {
  flex-direction: column;
}

.create-post-page__title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.create-post-page__header-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  color: #64748b;
  font-size: 13px;
  font-weight: 600;
}

.create-post-page__form {
  display: grid;
  gap: 8px;
}

.create-post-page__editor-grid {
  align-items: start;
}

.create-post-page__preview {
  min-height: 100%;
  padding: 18px;
  border-radius: 20px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  border: 1px solid rgba(148, 163, 184, 0.16);
}

.create-post-page__preview-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
  color: #64748b;
  font-size: 13px;
  font-weight: 700;
}

.create-post-page__preview-body h3 {
  margin: 0 0 16px;
  color: #0f172a;
  font-size: 24px;
}

.create-post-page__tips {
  display: grid;
  gap: 12px;
}

.create-post-page__tip {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 14px 16px;
  border-radius: 16px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.12);
  color: #475569;
}

.create-post-page__tip strong {
  color: #0f172a;
}

@media (max-width: 960px) {
  .create-post-page__hero-content,
  .create-post-page__hero-actions,
  .create-post-page__actions,
  .create-post-page__header {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>