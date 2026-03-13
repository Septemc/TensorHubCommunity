<template>
  <div class="admin-dashboard" v-loading="loading">
    <el-card class="admin-dashboard__hero">
      <div class="admin-dashboard__hero-top">
        <div class="admin-dashboard__hero-copy">
          <div class="admin-dashboard__eyebrow">Admin Console</div>
          <h1>社区后台管理</h1>
          <p>集中处理用户审核、角色分配、帖子运营、公告发布、板块管理和站点内容维护。</p>
        </div>
        <div class="admin-dashboard__hero-actions">
          <el-button type="primary" @click="loadAll">刷新数据</el-button>
          <el-button plain @click="activeTab = 'users'">处理审核</el-button>
        </div>
      </div>

      <div class="admin-dashboard__hero-stats">
        <div class="admin-dashboard__hero-stat">
          <span>待审核用户</span>
          <strong>{{ pendingUsers.length }}</strong>
          <small>需要尽快处理实名审核</small>
        </div>
        <div class="admin-dashboard__hero-stat">
          <span>帖子总量</span>
          <strong>{{ admin.posts.length }}</strong>
          <small>支持置顶、精华和删除等运营操作</small>
        </div>
        <div class="admin-dashboard__hero-stat">
          <span>公告总量</span>
          <strong>{{ admin.announcements.length }}</strong>
          <small>支持草稿与发布状态管理</small>
        </div>
        <div class="admin-dashboard__hero-stat">
          <span>板块数量</span>
          <strong>{{ admin.categories.length }}</strong>
          <small>统一维护论坛分区和排序</small>
        </div>
      </div>
    </el-card>

    <el-tabs v-model="activeTab" class="admin-dashboard__tabs">
      <el-tab-pane label="概览" name="overview">
        <div class="card-grid two">
          <el-card>
            <template #header><div class="section-title"><span>待审核用户</span></div></template>
            <el-empty v-if="!pendingUsers.length" description="暂无待审核用户" />
            <el-table v-else :data="pendingUsers" table-layout="auto">
              <el-table-column prop="username" label="用户名" />
              <el-table-column prop="real_name" label="实名" />
              <el-table-column prop="major" label="专业" />
              <el-table-column label="操作" width="220">
                <template #default="scope">
                  <el-space wrap>
                    <el-button size="small" @click="changeVerification(scope.row.id, 'approved')">通过</el-button>
                    <el-button size="small" type="danger" plain @click="changeVerification(scope.row.id, 'rejected')">驳回</el-button>
                  </el-space>
                </template>
              </el-table-column>
            </el-table>
          </el-card>

          <el-card>
            <template #header><div class="section-title"><span>最新帖子</span></div></template>
            <el-table :data="admin.posts.slice(0, 6)" table-layout="auto">
              <el-table-column prop="title" label="标题" min-width="220" />
              <el-table-column label="作者" width="120"><template #default="scope">{{ scope.row.author.username }}</template></el-table-column>
              <el-table-column label="运营状态" width="180">
                <template #default="scope">
                  <el-space wrap>
                    <el-tag v-if="scope.row.is_top" type="primary">置顶</el-tag>
                    <el-tag v-if="scope.row.is_essence" type="warning">精华</el-tag>
                    <el-tag v-if="!scope.row.is_top && !scope.row.is_essence" type="info">普通</el-tag>
                  </el-space>
                </template>
              </el-table-column>
            </el-table>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="用户审核" name="users">
        <el-card>
          <template #header><div class="section-title"><span>用户与角色管理</span></div></template>
          <el-table :data="admin.users" table-layout="auto">
            <el-table-column prop="username" label="用户名" width="140" />
            <el-table-column prop="real_name" label="实名" width="140" />
            <el-table-column prop="major" label="专业" min-width="160" />
            <el-table-column label="审核状态" width="120">
              <template #default="scope"><el-tag :type="verificationType(scope.row.verification_status)">{{ verificationLabel(scope.row.verification_status) }}</el-tag></template>
            </el-table-column>
            <el-table-column label="角色分配" min-width="260">
              <template #default="scope">
                <el-select v-model="roleSelections[scope.row.id]" multiple collapse-tags collapse-tags-tooltip style="width: 100%" @change="updateRoles(scope.row.id)">
                  <el-option v-for="role in admin.roles" :key="role.id" :label="role.display_name" :value="role.id" />
                </el-select>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="240">
              <template #default="scope">
                <el-space wrap>
                  <el-button size="small" @click="changeVerification(scope.row.id, 'approved')">通过</el-button>
                  <el-button size="small" type="warning" plain @click="changeVerification(scope.row.id, 'pending')">待定</el-button>
                  <el-button size="small" type="danger" plain @click="changeVerification(scope.row.id, 'rejected')">驳回</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="帖子管理" name="posts">
        <el-card>
          <template #header><div class="section-title"><span>帖子运营</span></div></template>
          <el-table :data="admin.posts" table-layout="auto">
            <el-table-column prop="title" label="标题" min-width="260" />
            <el-table-column label="作者" width="120"><template #default="scope">{{ scope.row.author.username }}</template></el-table-column>
            <el-table-column label="数据" width="180"><template #default="scope">赞 {{ scope.row.likes_count }} · 评 {{ scope.row.comments_count }} · 浏览 {{ scope.row.views }}</template></el-table-column>
            <el-table-column label="状态" width="160">
              <template #default="scope">
                <el-space wrap>
                  <el-tag v-if="scope.row.is_top" type="primary">置顶</el-tag>
                  <el-tag v-if="scope.row.is_essence" type="warning">精华</el-tag>
                </el-space>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="280">
              <template #default="scope">
                <el-space wrap>
                  <el-button size="small" @click="admin.flipTop(scope.row.id)">{{ scope.row.is_top ? '取消置顶' : '设为置顶' }}</el-button>
                  <el-button size="small" plain @click="admin.flipEssence(scope.row.id)">{{ scope.row.is_essence ? '取消精华' : '设为精华' }}</el-button>
                  <el-button size="small" @click="router.push(`/forum/post/${scope.row.id}`)">查看</el-button>
                  <el-button size="small" type="danger" plain @click="removeManagedPost(scope.row.id)">删除</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <el-tab-pane label="公告管理" name="announcements">
        <div class="card-grid two">
          <el-card>
            <template #header><div class="section-title"><span>{{ announcementForm.id ? '编辑公告' : '发布公告' }}</span></div></template>
            <el-form label-position="top" :model="announcementForm">
              <el-form-item label="标题"><el-input v-model="announcementForm.title" /></el-form-item>
              <el-form-item label="内容 Markdown"><el-input v-model="announcementForm.content" type="textarea" :rows="10" resize="vertical" /></el-form-item>
              <el-form-item label="封面图"><input type="file" accept="image/*" @change="onAnnouncementUpload" /></el-form-item>
              <el-form-item><el-switch v-model="announcementForm.is_published" active-text="已发布" inactive-text="草稿" /></el-form-item>
              <div class="admin-form-actions">
                <el-button type="primary" @click="saveAnnouncement">保存公告</el-button>
                <el-button @click="resetAnnouncementForm">清空</el-button>
              </div>
            </el-form>
          </el-card>
          <el-card>
            <template #header><div class="section-title"><span>公告列表</span></div></template>
            <div class="admin-list">
              <div v-for="item in admin.announcements" :key="item.id" class="admin-list-card">
                <div class="admin-list-card__head">
                  <strong>{{ item.title }}</strong>
                  <el-tag :type="item.is_published ? 'success' : 'info'">{{ item.is_published ? '已发布' : '草稿' }}</el-tag>
                </div>
                <p>{{ excerpt(item.content, 120) }}</p>
                <div class="admin-list-card__actions"><el-button text @click="editAnnouncement(item.id)">编辑</el-button></div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="板块管理" name="categories">
        <div class="card-grid two">
          <el-card>
            <template #header><div class="section-title"><span>{{ categoryForm.id ? '编辑板块' : '新建板块' }}</span></div></template>
            <el-form label-position="top" :model="categoryForm">
              <el-form-item label="板块名称"><el-input v-model="categoryForm.name" /></el-form-item>
              <el-form-item label="描述"><el-input v-model="categoryForm.description" type="textarea" :rows="4" /></el-form-item>
              <div class="card-grid two">
                <el-form-item label="类型">
                  <el-select v-model="categoryForm.type" style="width: 100%">
                    <el-option label="讨论" value="forum" />
                    <el-option label="竞赛" value="contest" />
                    <el-option label="项目招募" value="recruit_project" />
                    <el-option label="组队招募" value="recruit_team" />
                    <el-option label="公告" value="notice" />
                  </el-select>
                </el-form-item>
                <el-form-item label="排序"><el-input-number v-model="categoryForm.sort_order" :min="0" style="width: 100%" /></el-form-item>
              </div>
              <el-form-item><el-switch v-model="categoryForm.is_active" active-text="启用板块" inactive-text="停用板块" /></el-form-item>
              <div class="admin-form-actions">
                <el-button type="primary" @click="saveCategory">保存板块</el-button>
                <el-button @click="resetCategoryForm">清空</el-button>
              </div>
            </el-form>
          </el-card>
          <el-card>
            <template #header><div class="section-title"><span>板块列表</span></div></template>
            <div class="admin-list">
              <div v-for="item in admin.categories" :key="item.id" class="admin-list-card">
                <div class="admin-list-card__head">
                  <strong>{{ item.name }}</strong>
                  <el-tag :type="item.is_active ? 'success' : 'info'">{{ item.is_active ? '启用中' : '已停用' }}</el-tag>
                </div>
                <p>{{ item.description || '暂无描述' }}</p>
                <div class="admin-list-card__actions">
                  <el-tag size="small">{{ item.type }}</el-tag>
                  <el-button text @click="editCategory(item.id)">编辑</el-button>
                </div>
              </div>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <el-tab-pane label="站点内容" name="pages">
        <div class="card-grid two">
          <el-card>
            <template #header><div class="section-title"><span>首页内容</span></div></template>
            <el-form label-position="top" :model="pageForms.home">
              <el-form-item label="标题"><el-input v-model="pageForms.home.title" /></el-form-item>
              <el-form-item label="内容 Markdown"><el-input v-model="pageForms.home.content" type="textarea" :rows="12" resize="vertical" /></el-form-item>
              <el-form-item><el-switch v-model="pageForms.home.is_published" active-text="已发布" inactive-text="未发布" /></el-form-item>
              <el-button type="primary" @click="savePage('home')">保存首页</el-button>
            </el-form>
          </el-card>
          <el-card>
            <template #header><div class="section-title"><span>关于我们</span></div></template>
            <el-form label-position="top" :model="pageForms.about">
              <el-form-item label="标题"><el-input v-model="pageForms.about.title" /></el-form-item>
              <el-form-item label="内容 Markdown"><el-input v-model="pageForms.about.content" type="textarea" :rows="12" resize="vertical" /></el-form-item>
              <el-form-item><el-switch v-model="pageForms.about.is_published" active-text="已发布" inactive-text="未发布" /></el-form-item>
              <el-button type="primary" @click="savePage('about')">保存关于页</el-button>
            </el-form>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useRouter } from 'vue-router'

import { uploadImage } from '../../api/admin'
import { useAdminStore } from '../../stores/admin'
import { useForumStore } from '../../stores/forum'
import type { SitePage } from '../../types/models'

const admin = useAdminStore()
const forum = useForumStore()
const router = useRouter()

const activeTab = ref('overview')
const loading = ref(false)
const roleSelections = reactive<Record<number, number[]>>({})

const announcementForm = reactive({
  id: undefined as number | undefined,
  title: '',
  content: '',
  cover_image: '',
  is_published: true,
})

const categoryForm = reactive({
  id: undefined as number | undefined,
  name: '',
  description: '',
  type: 'forum',
  sort_order: 0,
  is_active: true,
})

const pageForms = reactive<Record<string, Partial<SitePage>>>({
  home: { title: 'TensorHub 首页', content: '', is_published: true },
  about: { title: '关于我们', content: '', is_published: true },
})

const pendingUsers = computed(() => admin.users.filter((item) => item.verification_status === 'pending'))

async function loadAll() {
  try {
    loading.value = true
    await Promise.all([
      admin.loadUsers(),
      admin.loadRoles(),
      admin.loadAnnouncements(),
      admin.loadPosts(),
      admin.loadCategories(),
    ])
    hydrateRoleSelections()
    await Promise.all([loadPageSafe('home'), loadPageSafe('about')])
  } finally {
    loading.value = false
  }
}

async function loadPageSafe(slug: 'home' | 'about') {
  try {
    const page = await admin.loadPage(slug)
    pageForms[slug] = { ...page }
  } catch {
    pageForms[slug] = {
      title: slug === 'home' ? 'TensorHub 首页' : '关于我们',
      content: '',
      is_published: true,
    }
  }
}

function hydrateRoleSelections() {
  admin.users.forEach((user) => {
    roleSelections[user.id] = user.roles.map((role) => role.id)
  })
}

async function changeVerification(userId: number, status: 'pending' | 'approved' | 'rejected') {
  await admin.setVerification(userId, status)
  hydrateRoleSelections()
  ElMessage.success('审核状态已更新')
}

async function updateRoles(userId: number) {
  await admin.setRoles(userId, roleSelections[userId] || [])
  ElMessage.success('角色分配已更新')
}

function verificationLabel(status: 'pending' | 'approved' | 'rejected') {
  return status === 'approved' ? '已通过' : status === 'rejected' ? '已驳回' : '待审核'
}

function verificationType(status: 'pending' | 'approved' | 'rejected') {
  return status === 'approved' ? 'success' : status === 'rejected' ? 'danger' : 'warning'
}

function resetAnnouncementForm() {
  announcementForm.id = undefined
  announcementForm.title = ''
  announcementForm.content = ''
  announcementForm.cover_image = ''
  announcementForm.is_published = true
}

function editAnnouncement(id: number) {
  const item = admin.announcements.find((announcement) => announcement.id === id)
  if (!item) return
  announcementForm.id = item.id
  announcementForm.title = item.title
  announcementForm.content = item.content
  announcementForm.cover_image = item.cover_image || ''
  announcementForm.is_published = item.is_published
}

async function onAnnouncementUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const result = await uploadImage(file)
  announcementForm.cover_image = result.url
  ElMessage.success('封面图上传成功')
}

async function saveAnnouncement() {
  await admin.saveAnnouncement({ ...announcementForm })
  ElMessage.success('公告已保存')
  resetAnnouncementForm()
}

function resetCategoryForm() {
  categoryForm.id = undefined
  categoryForm.name = ''
  categoryForm.description = ''
  categoryForm.type = 'forum'
  categoryForm.sort_order = 0
  categoryForm.is_active = true
}

function editCategory(id: number) {
  const item = admin.categories.find((category) => category.id === id)
  if (!item) return
  categoryForm.id = item.id
  categoryForm.name = item.name
  categoryForm.description = item.description || ''
  categoryForm.type = item.type
  categoryForm.sort_order = item.sort_order
  categoryForm.is_active = item.is_active
}

async function saveCategory() {
  await admin.saveCategory({ ...categoryForm })
  ElMessage.success('板块已保存')
  resetCategoryForm()
}

async function savePage(slug: 'home' | 'about') {
  await admin.savePage(slug, pageForms[slug])
  ElMessage.success(slug === 'home' ? '首页内容已保存' : '关于页已保存')
}

async function removeManagedPost(postId: number) {
  try {
    await ElMessageBox.confirm('确认删除这篇帖子？', '删除帖子', { type: 'warning' })
    await forum.removePost(postId)
    await admin.loadPosts()
    ElMessage.success('帖子已删除')
  } catch (error) {
    if (error !== 'cancel') {
      const message = axios.isAxiosError(error)
        ? (error.response?.data?.detail ?? '删除失败')
        : '删除失败'
      ElMessage.error(message)
    }
  }
}

function excerpt(content: string, max = 100) {
  return content.replace(/[#>*_`-]/g, ' ').replace(/\s+/g, ' ').trim().slice(0, max) || '暂无内容'
}

onMounted(loadAll)
</script>

<style scoped>
.admin-dashboard {
  display: grid;
  gap: 20px;
}

.admin-dashboard__hero {
  background:
    radial-gradient(circle at top right, rgba(59, 130, 246, 0.18), transparent 28%),
    linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(241, 245, 249, 0.95));
}

.admin-dashboard__hero-top,
.admin-dashboard__hero-actions,
.admin-form-actions,
.admin-list-card__head,
.admin-list-card__actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.admin-dashboard__hero-copy {
  max-width: 720px;
}

.admin-dashboard__eyebrow {
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

.admin-dashboard__hero h1 {
  margin: 16px 0 12px;
  font-size: clamp(28px, 4vw, 40px);
  line-height: 1.1;
}

.admin-dashboard__hero p,
.admin-dashboard__hero-stat small,
.admin-list-card p {
  margin: 0;
  color: #64748b;
  line-height: 1.7;
}

.admin-dashboard__hero-stats {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-top: 20px;
}

.admin-dashboard__hero-stat {
  padding: 16px 18px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.admin-dashboard__hero-stat span,
.admin-dashboard__hero-stat small {
  display: block;
}

.admin-dashboard__hero-stat strong {
  display: block;
  margin: 8px 0;
  font-size: 30px;
  color: #0f172a;
}

.admin-dashboard__tabs :deep(.el-tabs__header) {
  margin-bottom: 18px;
}

.admin-list {
  display: grid;
  gap: 14px;
}

.admin-list-card {
  padding: 16px 18px;
  border-radius: 18px;
  background: #f8fafc;
  border: 1px solid rgba(148, 163, 184, 0.14);
}

.admin-list-card strong {
  color: #0f172a;
}

@media (max-width: 1100px) {
  .admin-dashboard__hero-stats {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 960px) {
  .admin-dashboard__hero-top,
  .admin-dashboard__hero-actions,
  .admin-form-actions,
  .admin-list-card__head,
  .admin-list-card__actions {
    flex-direction: column;
    align-items: stretch;
  }

  .admin-dashboard__hero-actions :deep(.el-button) {
    width: 100%;
  }
}

@media (max-width: 640px) {
  .admin-dashboard__hero-stats {
    grid-template-columns: 1fr;
  }
}
</style>