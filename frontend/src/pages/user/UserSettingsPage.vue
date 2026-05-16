<template>
  <div class="px-4 py-4 md:px-0 md:py-6 pb-20 lg:pb-4">
    <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
      <i class="fas fa-cog text-[#0064FF]"></i> 个人设置
    </h2>

    <div v-if="auth.user" class="space-y-4">
      <!-- Avatar & Username -->
      <div class="content-card p-4 md:p-5 shadow-sm">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-14 h-14 bg-[#0064FF] rounded-full flex items-center justify-center text-white text-lg font-bold">
            {{ auth.user.username.slice(0, 2).toUpperCase() }}
          </div>
          <div>
            <div class="font-bold text-gray-900">{{ auth.user.username }}</div>
            <div class="text-[12px] text-gray-400 flex items-center gap-1">
              <template v-for="role in auth.user.roles" :key="role.id">
                <span class="px-1.5 py-0.5 rounded-sm text-[10px]" :style="{ color: role.color || '#5F6368', backgroundColor: (role.color || '#5F6368') + '15' }">{{ role.display_name }}</span>
              </template>
            </div>
            <div class="text-[11px] text-gray-400 mt-0.5">
              {{ auth.user.verification_status === 'approved' ? '✓ 已认证' : auth.user.verification_status === 'pending' ? '⏳ 待审核' : '未认证' }}
            </div>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-2 text-[13px] text-gray-600">
          <div>邮箱：{{ auth.user.email || '未设置' }}</div>
          <div>专业：{{ auth.user.major || '未设置' }}</div>
          <div>学号：{{ auth.user.student_id || '未设置' }}</div>
          <div>性别：{{ genderMap[auth.user.gender || ''] || '未设置' }}</div>
        </div>
      </div>

      <!-- Edit Form -->
      <div class="content-card p-4 md:p-5 shadow-sm">
        <h3 class="font-bold text-[14px] text-gray-800 mb-3">编辑资料</h3>
        <form @submit.prevent="saveProfile" class="space-y-3">
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">真实姓名</label>
            <input v-model="form.real_name" type="text"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF]" />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">邮箱</label>
            <input v-model="form.email" type="email"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF]" />
          </div>
          <div>
            <label class="block text-[13px] font-medium text-gray-600 mb-1">专业</label>
            <input v-model="form.major" type="text"
              class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF]" />
          </div>
          <button type="submit" :disabled="saving"
            class="bg-[#0064FF] hover:bg-[#0052D9] text-white px-4 py-1.5 rounded-sm text-[13px] font-medium disabled:opacity-50">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <span v-if="saved" class="text-green-600 text-[13px] ml-2">✓ 已保存</span>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const saving = ref(false)
const saved = ref(false)

const genderMap: Record<string, string> = { male: '男', female: '女', other: '其他' }

const form = reactive({
  real_name: '',
  email: '',
  major: '',
})

onMounted(() => {
  if (auth.user) {
    form.real_name = auth.user.real_name || ''
    form.email = auth.user.email || ''
    form.major = auth.user.major || ''
  }
})

async function saveProfile() {
  saving.value = true
  saved.value = false
  try {
    await auth.saveProfile(form)
    saved.value = true
    setTimeout(() => { saved.value = false }, 2000)
  } catch {
    // ignore
  } finally {
    saving.value = false
  }
}
</script>