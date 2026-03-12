<template>
  <el-tabs v-model="activeTab">
    <el-tab-pane label="概览" name="overview">
      <div class="card-grid two">
        <el-card>
          <div class="section-title"><span>用户审核</span><el-button @click="loadAll">刷新</el-button></div>
          <el-table :data="admin.users">
            <el-table-column prop="username" label="用户名" />
            <el-table-column prop="real_name" label="实名" />
            <el-table-column prop="verification_status" label="审核状态" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-space>
                  <el-button size="small" @click="admin.setVerification(scope.row.id, 'approved')">通过</el-button>
                  <el-button size="small" type="danger" @click="admin.setVerification(scope.row.id, 'rejected')">驳回</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card>
          <div class="section-title"><span>帖子管理</span></div>
          <el-table :data="admin.posts">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="is_top" label="置顶" />
            <el-table-column prop="is_essence" label="精华" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-space>
                  <el-button size="small" @click="admin.flipTop(scope.row.id)">切换置顶</el-button>
                  <el-button size="small" @click="admin.flipEssence(scope.row.id)">切换精华</el-button>
                </el-space>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </div>
    </el-tab-pane>

    <el-tab-pane label="公告管理" name="announcements">
      <div class="card-grid two">
        <el-card>
          <div class="section-title"><span>发布公告</span></div>
          <el-form label-position="top" :model="announcementForm">
            <el-form-item label="标题"><el-input v-model="announcementForm.title" /></el-form-item>
            <el-form-item label="内容 Markdown"><el-input v-model="announcementForm.content" type="textarea" :rows="8" /></el-form-item>
            <el-form-item label="封面图">
              <input type="file" accept="image/*" @change="onAnnouncementUpload" />
            </el-form-item>
            <el-button type="primary" @click="saveAnnouncement">保存公告</el-button>
          </el-form>
        </el-card>

        <el-card>
          <div class="section-title"><span>公告列表</span></div>
          <el-table :data="admin.announcements">
            <el-table-column prop="title" label="标题" />
            <el-table-column prop="is_published" label="发布中" />
          </el-table>
        </el-card>
      </div>
    </el-tab-pane>

    <el-tab-pane label="站点内容" name="pages">
      <div class="card-grid two">
        <el-card>
          <div class="section-title"><span>编辑 about 页面</span></div>
          <el-form label-position="top" :model="pageForm">
            <el-form-item label="标题"><el-input v-model="pageForm.title" /></el-form-item>
            <el-form-item label="内容 Markdown"><el-input v-model="pageForm.content" type="textarea" :rows="10" /></el-form-item>
            <el-button type="primary" @click="savePage">保存页面</el-button>
          </el-form>
        </el-card>

        <el-card>
          <div class="section-title"><span>新建板块</span></div>
          <el-form label-position="top" :model="categoryForm">
            <el-form-item label="板块名"><el-input v-model="categoryForm.name" /></el-form-item>
            <el-form-item label="描述"><el-input v-model="categoryForm.description" /></el-form-item>
            <el-form-item label="类型"><el-input v-model="categoryForm.type" /></el-form-item>
            <el-button type="primary" @click="saveCategory">保存板块</el-button>
          </el-form>
        </el-card>
      </div>
    </el-tab-pane>
  </el-tabs>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { uploadImage } from '../../api/admin'
import { useAdminStore } from '../../stores/admin'

const admin = useAdminStore()
const activeTab = ref('overview')

const announcementForm = reactive({
  title: '',
  content: '',
  cover_image: '',
  is_published: true,
})

const pageForm = reactive({ title: '', content: '', is_published: true })
const categoryForm = reactive({ name: '', description: '', type: 'forum', sort_order: 0, is_active: true })

async function loadAll() {
  await Promise.all([admin.loadUsers(), admin.loadAnnouncements(), admin.loadPosts()])
  try {
    const about = await admin.loadPage('about')
    pageForm.title = about.title
    pageForm.content = about.content
    pageForm.is_published = about.is_published
  } catch {
    pageForm.title = '关于 TensorHub'
    pageForm.content = ''
  }
}

async function onAnnouncementUpload(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const result = await uploadImage(file)
  announcementForm.cover_image = result.url
}

async function saveAnnouncement() {
  await admin.saveAnnouncement(announcementForm)
  announcementForm.title = ''
  announcementForm.content = ''
  announcementForm.cover_image = ''
  ElMessage.success('公告已保存')
}

async function savePage() {
  await admin.savePage('about', pageForm)
  ElMessage.success('页面已保存')
}

async function saveCategory() {
  await admin.saveCategory(categoryForm)
  categoryForm.name = ''
  categoryForm.description = ''
  ElMessage.success('板块已保存')
}

onMounted(loadAll)
</script>
