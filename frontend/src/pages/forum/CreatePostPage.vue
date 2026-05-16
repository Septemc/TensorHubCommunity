<template>
  <div class="px-4 py-4 md:px-0 md:py-6 pb-20 lg:pb-4">
    <h2 class="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
      <i class="fas fa-pen text-[#0064FF]"></i> 发布帖子
    </h2>

    <div v-if="!auth.isAuthenticated" class="content-card p-6 text-center shadow-sm">
      <i class="fas fa-lock text-3xl text-gray-300 mb-3"></i>
      <p class="text-gray-500 mb-3">请先登录后再发帖</p>
      <router-link to="/login" class="inline-block bg-[#0064FF] text-white px-4 py-1.5 rounded-sm text-[13px] font-medium">去登录</router-link>
    </div>

    <form v-else @submit.prevent="submit" class="space-y-4">
      <div class="content-card p-4 md:p-5 shadow-sm">
        <div class="mb-4">
          <label class="block text-[13px] font-medium text-gray-600 mb-1">分类</label>
          <select v-model="form.category_id" required
            class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF] bg-white">
            <option value="" disabled>请选择分类</option>
            <option v-for="cat in categories" :key="cat.id" :value="cat.id">{{ cat.name }}</option>
          </select>
        </div>
        <div class="mb-4">
          <label class="block text-[13px] font-medium text-gray-600 mb-1">标题</label>
          <input v-model="form.title" type="text" placeholder="请输入标题" required
            class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] focus:outline-none focus:border-[#0064FF]" />
        </div>
        <div>
          <label class="block text-[13px] font-medium text-gray-600 mb-1">内容</label>
          <div class="mb-2 flex gap-1">
            <button type="button" @click="insertMarkdown('**', '**')" class="px-2 py-1 bg-gray-100 rounded-sm text-[12px] text-gray-600 hover:bg-gray-200"><i class="fas fa-bold"></i></button>
            <button type="button" @click="insertMarkdown('## ', '')" class="px-2 py-1 bg-gray-100 rounded-sm text-[12px] text-gray-600 hover:bg-gray-200"><i class="fas fa-heading"></i></button>
            <button type="button" @click="insertMarkdown('`', '`')" class="px-2 py-1 bg-gray-100 rounded-sm text-[12px] text-gray-600 hover:bg-gray-200"><i class="fas fa-code"></i></button>
            <button type="button" @click="insertMarkdown('- ', '')" class="px-2 py-1 bg-gray-100 rounded-sm text-[12px] text-gray-600 hover:bg-gray-200"><i class="fas fa-list-ul"></i></button>
            <button type="button" @click="insertMarkdown('[链接](', ')')" class="px-2 py-1 bg-gray-100 rounded-sm text-[12px] text-gray-600 hover:bg-gray-200"><i class="fas fa-link"></i></button>
          </div>
          <textarea ref="contentRef" v-model="form.content" rows="12" placeholder="支持 Markdown 格式..." required
            class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] resize-none focus:outline-none focus:border-[#0064FF] font-mono"></textarea>
        </div>
      </div>

      <div v-if="error" class="bg-red-50 border border-red-200 text-red-600 text-[13px] px-3 py-2 rounded-sm">{{ error }}</div>

      <div class="flex justify-end">
        <button type="submit" :disabled="submitting"
          class="bg-[#0064FF] hover:bg-[#0052D9] text-white px-6 py-2 rounded-sm text-[14px] font-medium disabled:opacity-50 transition-all">
          {{ submitting ? '发布中...' : '发布帖子' }}
        </button>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../../stores/auth'
import { fetchCategories, createPost } from '../../api/forum'
import type { Category } from '../../types/models'

const auth = useAuthStore()
const router = useRouter()
const categories = ref<Category[]>([])
const error = ref('')
const submitting = ref(false)
const contentRef = ref<HTMLTextAreaElement | null>(null)

const form = reactive({
  title: '',
  content: '',
  category_id: '' as string | number,
  post_type: 'forum',
})

function insertMarkdown(prefix: string, suffix: string) {
  const el = contentRef.value
  if (!el) return
  const start = el.selectionStart
  const end = el.selectionEnd
  const text = form.content
  const selected = text.slice(start, end)
  form.content = text.slice(0, start) + prefix + selected + suffix + text.slice(end)
  el.focus()
  el.setSelectionRange(start + prefix.length, start + prefix.length + selected.length)
}

onMounted(async () => {
  try { categories.value = await fetchCategories() } catch { /* ignore */ }
})

async function submit() {
  error.value = ''
  submitting.value = true
  try {
    const data = {
      ...form,
      category_id: Number(form.category_id),
    }
    const post = await createPost(data)
    router.push(`/forum/post/${post.id}`)
  } catch (e: any) {
    error.value = e?.response?.data?.detail || '发布失败'
  } finally {
    submitting.value = false
  }
}
</script>