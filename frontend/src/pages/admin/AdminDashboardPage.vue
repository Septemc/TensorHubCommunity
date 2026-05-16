<template>
  <div class="px-4 py-4 md:px-0 md:py-6 pb-20 lg:pb-4">
    <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
      <i class="fas fa-shield-alt text-[#0064FF]"></i> 管理后台
    </h2>

    <div v-if="!auth.isAdmin" class="content-card p-6 text-center shadow-sm">
      <i class="fas fa-exclamation-triangle text-3xl text-gray-300 mb-3"></i>
      <p class="text-gray-500">您没有管理权限</p>
    </div>

    <template v-else>
      <!-- Stats Cards -->
      <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <div class="content-card p-4 shadow-sm">
          <div class="text-[12px] text-gray-400 mb-1">用户数</div>
          <div class="text-xl font-bold text-gray-900">{{ stats.users }}</div>
        </div>
        <div class="content-card p-4 shadow-sm">
          <div class="text-[12px] text-gray-400 mb-1">帖子数</div>
          <div class="text-xl font-bold text-gray-900">{{ stats.posts }}</div>
        </div>
        <div class="content-card p-4 shadow-sm">
          <div class="text-[12px] text-gray-400 mb-1">评论数</div>
          <div class="text-xl font-bold text-gray-900">{{ stats.comments }}</div>
        </div>
        <div class="content-card p-4 shadow-sm">
          <div class="text-[12px] text-gray-400 mb-1">分类数</div>
          <div class="text-xl font-bold text-gray-900">{{ stats.categories }}</div>
        </div>
      </div>

      <!-- User Management -->
      <div class="content-card p-4 md:p-5 shadow-sm mb-4">
        <h3 class="font-bold text-[14px] text-gray-800 mb-3">用户管理</h3>
        <div v-if="loading" class="text-center py-8 text-gray-400"><i class="fas fa-spinner fa-spin"></i></div>
        <div v-else-if="users.length" class="overflow-x-auto">
          <table class="w-full text-[13px]">
            <thead>
              <tr class="border-b border-gray-100">
                <th class="text-left py-2 text-gray-500 font-medium">用户名</th>
                <th class="text-left py-2 text-gray-500 font-medium">学号</th>
                <th class="text-left py-2 text-gray-500 font-medium">专业</th>
                <th class="text-left py-2 text-gray-500 font-medium">状态</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.id" class="border-b border-gray-50">
                <td class="py-2">{{ user.username }}</td>
                <td class="py-2 text-gray-500">{{ user.student_id || '-' }}</td>
                <td class="py-2 text-gray-500">{{ user.major || '-' }}</td>
                <td class="py-2">
                  <span class="text-[10px] px-1.5 py-0.5 rounded-sm"
                    :class="user.verification_status === 'approved' ? 'bg-green-50 text-green-600' : user.verification_status === 'pending' ? 'bg-yellow-50 text-yellow-600' : 'bg-red-50 text-red-600'">
                    {{ statusMap[user.verification_status] || user.verification_status }}
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        <div v-else class="text-center py-6 text-gray-400 text-[13px]">暂无用户数据</div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/client'

const auth = useAuthStore()
const loading = ref(true)
const users = ref<any[]>([])
const stats = reactive({ users: 0, posts: 0, comments: 0, categories: 0 })

const statusMap: Record<string, string> = { pending: '待审核', approved: '已认证', rejected: '已拒绝' }

onMounted(async () => {
  if (!auth.isAdmin) return
  try {
    const [u, p, c, cats] = await Promise.all([
      api.get('/admin/users').then(r => r.data),
      api.get('/admin/stats/posts').then(r => r.data).catch(() => ({})),
      api.get('/admin/stats/comments').then(r => r.data).catch(() => ({})),
      api.get('/categories').then(r => r.data),
    ])
    users.value = Array.isArray(u) ? u : u.items || []
    stats.users = users.value.length
    stats.posts = p.total || 0
    stats.comments = c.total || 0
    stats.categories = Array.isArray(cats) ? cats.length : (cats.items || []).length
  } catch { /* ignore */ } finally { loading.value = false }
})
</script>