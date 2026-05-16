<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4 py-8">
    <div class="w-full max-w-sm">
      <div class="content-card p-6 md:p-8 shadow-sm">
        <h2 class="text-xl font-bold text-gray-900 text-center mb-6">登录 TensorHub</h2>

        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 text-[13px] px-3 py-2 rounded-sm mb-4">
          {{ error }}
        </div>

        <form @submit.prevent="submit" class="space-y-4">
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">用户名或邮箱</label>
            <input
              v-model="form.identifier"
              type="text"
              placeholder="请输入用户名或邮箱"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors"
              required
            />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">密码</label>
            <input
              v-model="form.password"
              type="password"
              placeholder="请输入密码"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors"
              required
            />
          </div>
          <button
            type="submit"
            :disabled="submitting"
            class="w-full bg-[#0064FF] hover:bg-[#0052D9] text-white py-2 rounded-sm text-[14px] font-medium transition-all disabled:opacity-50"
          >
            {{ submitting ? '登录中...' : '登录' }}
          </button>
        </form>

        <div class="mt-4 text-center text-[12px] text-gray-400">
          还没有账号？
          <router-link to="/register" class="text-[#0064FF] hover:underline">立即注册</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const error = ref('')
const submitting = ref(false)
const form = reactive({ identifier: '', password: '' })

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.doLogin(form)
    router.push('/')
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    if (detail) {
      error.value = typeof detail === 'string' ? detail : '登录失败'
    } else {
      error.value = '登录失败，请检查后端与数据库配置'
    }
  } finally {
    submitting.value = false
  }
}
</script>