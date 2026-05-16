<template>
  <div class="overflow-x-hidden pb-16 lg:pb-0">
    <div v-if="loading" class="text-center py-12 text-gray-400"><i class="fas fa-spinner fa-spin text-2xl"></i></div>

    <template v-else-if="post">
      <!-- Header Info -->
      <div class="px-4 py-2 md:px-0 md:mb-4">
        <div class="flex items-center gap-2 mb-2">
          <router-link to="/forum" class="text-[#0064FF] text-[13px]"><i class="fas fa-arrow-left mr-1"></i>返回</router-link>
        </div>
        <div class="flex flex-wrap gap-1.5 items-center mb-2">
          <router-link :to="`/forum/category/${post.category_id}`" class="flex items-center gap-1 text-[10px] px-1.5 py-0.5 rounded-sm border"
            :class="categoryColor">{{ categoryName }}</router-link>
          <span v-if="post.is_top" class="text-[10px] px-1.5 py-0.5 rounded-sm bg-red-50 text-red-600 border border-red-100">置顶</span>
          <span v-if="post.is_essence" class="text-[10px] px-1.5 py-0.5 rounded-sm bg-yellow-50 text-yellow-600 border border-yellow-100">精华</span>
        </div>
        <h1 class="text-lg md:text-2xl font-bold text-gray-900 leading-snug">{{ post.title }}</h1>
      </div>

      <div class="flex flex-col xl:flex-row gap-4">
        <!-- Post Content -->
        <div class="flex-1 space-y-2 md:space-y-4">
          <div class="content-card p-4 md:p-5 shadow-sm relative">
            <!-- Author Header -->
            <div class="flex items-center gap-3 mb-4">
              <div class="shrink-0">
                <div class="w-10 h-10 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-sm border border-indigo-200">
                  {{ post.author?.username?.slice(0, 2).toUpperCase() || 'U' }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <div class="flex justify-between items-center">
                  <div class="flex flex-col">
                    <span class="font-bold text-gray-800 text-[14px]">{{ post.author?.username }}</span>
                    <span class="text-[11px] text-gray-400">{{ timeAgo(post.created_at) }}</span>
                  </div>
                  <span class="text-[11px] text-gray-400">{{ post.views }} 浏览</span>
                </div>
              </div>
            </div>

            <!-- Post Body -->
            <div class="markdown-body text-[15px] text-gray-700 leading-relaxed" v-html="renderedContent"></div>

            <!-- Post Actions -->
            <div class="flex items-center gap-6 mt-6 pt-4 border-t border-gray-50">
              <button @click="toggleLike" class="flex items-center gap-1.5 text-[13px] transition-colors"
                :class="post.is_liked ? 'text-[#0064FF]' : 'text-gray-400 hover:text-[#0064FF]'">
                <i :class="post.is_liked ? 'fas fa-thumbs-up' : 'far fa-thumbs-up'"></i> {{ post.likes_count }}
              </button>
              <span class="flex items-center gap-1.5 text-gray-400 text-[13px]"><i class="far fa-comment"></i> {{ comments.length }}</span>
              <button v-if="isAuthor" @click="handleDelete" class="text-gray-400 hover:text-red-500 ml-auto text-[13px]">
                <i class="fas fa-trash-alt"></i>
              </button>
            </div>
          </div>

          <!-- Comments Section -->
          <div class="content-card p-4 md:p-5 shadow-sm">
            <h3 class="font-bold text-[14px] text-gray-800 mb-4">评论 ({{ comments.length }})</h3>

            <!-- Comment Input -->
            <div v-if="auth.isAuthenticated" class="mb-4">
              <textarea v-model="commentContent" rows="3" placeholder="写下你的评论..."
                class="w-full px-3 py-2 border border-gray-200 rounded-sm text-[14px] resize-none focus:outline-none focus:border-[#0064FF] transition-colors"></textarea>
              <div class="flex justify-end mt-2">
                <button @click="submitComment" :disabled="submittingComment || !commentContent.trim()"
                  class="bg-[#0064FF] hover:bg-[#0052D9] text-white px-3 py-1 rounded-sm text-[12px] font-medium disabled:opacity-50 transition-all">
                  {{ submittingComment ? '发送中...' : '发表评论' }}
                </button>
              </div>
            </div>

            <!-- Comments List -->
            <div v-if="comments.length" class="space-y-4">
              <div v-for="comment in comments" :key="comment.id" class="border-b border-gray-50 pb-4 last:border-b-0">
                <div class="flex items-center gap-2 mb-2">
                  <div class="w-7 h-7 bg-indigo-100 rounded-full flex items-center justify-center text-indigo-600 font-bold text-[10px] border border-indigo-200">
                    {{ comment.author?.username?.slice(0, 2).toUpperCase() || 'U' }}
                  </div>
                  <span class="font-medium text-[13px] text-gray-800">{{ comment.author?.username }}</span>
                  <span class="text-[11px] text-gray-400 ml-auto">{{ timeAgo(comment.created_at) }}</span>
                </div>
                <div class="text-[13px] text-gray-700 pl-9 markdown-body" v-html="renderMarkdown(comment.content)"></div>
              </div>
            </div>
            <div v-else class="text-center py-6 text-gray-400 text-[13px]">暂无评论</div>
          </div>
        </div>
      </div>
    </template>

    <!-- Post Not Found -->
    <div v-else class="text-center py-12 text-gray-400">
      <i class="fas fa-exclamation-circle text-4xl mb-3"></i>
      <p>帖子不存在或已被删除</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchPost, fetchComments, createComment, togglePostLike, deletePost } from '../../api/forum'
import { fetchCategories } from '../../api/forum'
import { useAuthStore } from '../../stores/auth'
import { renderMarkdown } from '../../utils/content'
import type { Post, Comment as CommentType, Category } from '../../types/models'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const post = ref<Post | null>(null)
const comments = ref<CommentType[]>([])
const categories = ref<Category[]>([])
const loading = ref(true)
const commentContent = ref('')
const submittingComment = ref(false)

const isAuthor = computed(() => auth.user?.id === post.value?.user_id)

const categoryName = computed(() => {
  const cat = categories.value.find(c => c.id === post.value?.category_id)
  return cat?.name || '话题'
})

const categoryColor = computed(() => {
  const type = categories.value.find(c => c.id === post.value?.category_id)?.type || 'forum'
  const s: Record<string, string> = {
    forum: 'text-green-600 bg-green-50 border-green-100',
    contest: 'text-orange-600 bg-orange-50 border-orange-100',
    recruit_project: 'text-blue-600 bg-blue-50 border-blue-100',
    recruit_team: 'text-purple-600 bg-purple-50 border-purple-100',
    notice: 'text-red-600 bg-red-50 border-red-100',
  }
  return s[type] || 'text-gray-600 bg-gray-50 border-gray-100'
})

const renderedContent = computed(() => {
  if (!post.value) return ''
  return renderMarkdown(post.value.content)
})

function timeAgo(date?: string) {
  if (!date) return ''
  const diff = Date.now() - new Date(date).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 60) return `${mins} 分钟前`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours} 小时前`
  const days = Math.floor(hours / 24)
  if (days < 30) return `${days} 天前`
  return new Date(date).toLocaleDateString()
}

async function toggleLike() {
  if (!post.value) return
  try {
    const res = await togglePostLike(post.value.id)
    post.value.is_liked = res.liked
    post.value.likes_count = res.likes_count
  } catch { /* ignore */ }
}

async function submitComment() {
  if (!post.value || !commentContent.value.trim()) return
  submittingComment.value = true
  try {
    const newComment = await createComment(post.value.id, { content: commentContent.value })
    comments.value.push(newComment)
    commentContent.value = ''
  } catch { /* ignore */ } finally { submittingComment.value = false }
}

async function handleDelete() {
  if (!post.value) return
  if (!confirm('确定要删除此帖？')) return
  try {
    await deletePost(post.value.id)
    router.push('/forum')
  } catch { /* ignore */ }
}

onMounted(async () => {
  const postId = Number(route.params.id)
  try {
    const [p, c, cats] = await Promise.all([fetchPost(postId), fetchComments(postId), fetchCategories()])
    post.value = p
    comments.value = c
    categories.value = cats
  } catch { /* ignore */ } finally { loading.value = false }
})
</script>