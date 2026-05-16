<template>
  <div class="min-h-[60vh] flex items-center justify-center px-4 py-8">
    <div class="w-full max-w-sm">
      <div class="content-card p-6 md:p-8 shadow-sm">
        <h2 class="text-xl font-bold text-gray-900 text-center mb-6">注册 TensorHub</h2>

        <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 text-[13px] px-3 py-2 rounded-sm mb-4">
          {{ error }}
        </div>

        <form @submit.prevent="submit" class="space-y-3">
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">用户名</label>
            <input v-model="form.username" type="text" placeholder="请输入用户名"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors" required />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">真实姓名</label>
            <input v-model="form.real_name" type="text" placeholder="请输入真实姓名"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors" required />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">邮箱</label>
            <input v-model="form.email" type="email" placeholder="请输入邮箱（选填）"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors" />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">学号</label>
            <input v-model="form.student_id" type="text" placeholder="请输入学号"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors" required />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">专业</label>
            <input v-model="form.major" type="text" placeholder="请输入专业"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors" required />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">性别</label>
            <select v-model="form.gender"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors bg-white" required>
              <option value="">请选择</option>
              <option value="male">男</option>
              <option value="female">女</option>
              <option value="other">其他</option>
            </select>
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">密码</label>
            <input v-model="form.password" type="password" placeholder="请输入密码"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] transition-colors" required />
          </div>
          <button type="submit" :disabled="submitting"
            class="w-full bg-[#0064FF] hover:bg-[#0052D9] text-white py-2 rounded-sm text-[14px] font-medium transition-all disabled:opacity-50">
            {{ submitting ? '注册中...' : '注册' }}
          </button>
        </form>

        <div class="mt-4 text-center text-[12px] text-gray-400">
          已有账号？
          <router-link to="/login" class="text-[#0064FF] hover:underline">立即登录</router-link>
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
const form = reactive({
  username: '',
  password: '',
  email: '',
  real_name: '',
  gender: '',
  major: '',
  student_id: '',
})

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    await auth.doRegister(form)
    router.push('/login')
  } catch (e: any) {
    const detail = e?.response?.data?.detail
    error.value = detail ? (typeof detail === 'string' ? detail : '注册失败') : '注册失败'
  } finally {
    submitting.value = false
  }
}
</script>