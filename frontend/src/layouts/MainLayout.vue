<template>
  <div class="min-h-screen bg-[#F7F9FA]">
    <!-- Header -->
    <header class="h-12 bg-white border-b border-gray-200 flex items-center justify-between px-3 md:px-4 sticky top-0 z-50 nav-shadow">
      <div class="flex items-center gap-3">
        <button class="lg:hidden p-1 text-gray-500" @click="sidebarOpen = !sidebarOpen">
          <i class="fas fa-bars"></i>
        </button>
        <router-link to="/" class="flex items-center gap-1.5 cursor-pointer">
          <div class="w-6 h-6 bg-[#0064FF] rounded-sm flex items-center justify-center">
            <i class="fas fa-layer-group text-white text-[10px]"></i>
          </div>
          <span class="font-bold text-sm md:text-base text-gray-800 tracking-tight">TensorHub</span>
        </router-link>
      </div>
      <div class="flex items-center gap-2">
        <template v-if="auth.isAuthenticated">
          <router-link to="/forum/create" class="hidden md:flex items-center gap-1 bg-[#0064FF] hover:bg-[#0052D9] text-white px-3 py-1 rounded-sm text-[12px] font-medium transition-all">
            <i class="fas fa-pen text-[10px]"></i> 发帖
          </router-link>
          <div class="relative" ref="userMenuRef">
            <button @click="userMenuOpen = !userMenuOpen" class="flex items-center gap-2">
              <div class="w-7 h-7 bg-[#0064FF] rounded-full flex items-center justify-center text-white text-xs font-bold">
                {{ avatarText }}
              </div>
            </button>
            <div v-if="userMenuOpen" class="absolute right-0 top-10 bg-white border border-gray-200 rounded shadow-lg py-1 w-36 z-50">
              <router-link to="/user/settings" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" @click="userMenuOpen = false">
                <i class="fas fa-cog mr-2 text-gray-400"></i>设置
              </router-link>
              <router-link v-if="auth.isAdmin" to="/admin" class="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-50" @click="userMenuOpen = false">
                <i class="fas fa-shield-alt mr-2 text-gray-400"></i>管理
              </router-link>
              <button @click="handleLogout" class="w-full text-left px-4 py-2 text-sm text-red-500 hover:bg-gray-50">
                <i class="fas fa-sign-out-alt mr-2"></i>退出
              </button>
            </div>
          </div>
        </template>
        <template v-else>
          <router-link to="/login" class="bg-[#0064FF] hover:bg-[#0052D9] text-white px-3 py-1 rounded-sm text-[12px] font-medium transition-all">
            登录
          </router-link>
        </template>
      </div>
    </header>

    <!-- Mobile Sidebar Overlay -->
    <div v-if="sidebarOpen" class="fixed inset-0 bg-black/30 z-40 lg:hidden" @click="sidebarOpen = false"></div>

    <div class="flex max-w-[1400px] mx-auto min-h-[calc(100vh-3rem)]">
      <!-- Sidebar -->
      <aside :class="[sidebarOpen ? 'translate-x-0' : '-translate-x-full', 'lg:translate-x-0']" class="fixed lg:static z-40 lg:z-auto w-44 bg-white border-r border-gray-200 sticky top-12 h-[calc(100vh-3rem)] overflow-y-auto transition-transform duration-200">
        <div class="py-3">
          <div class="px-4 mb-2">
            <h3 class="text-[10px] font-bold text-gray-400 uppercase tracking-wider text-center lg:text-left">导航</h3>
          </div>
          <nav class="space-y-0.5">
            <router-link
              v-for="cat in categories"
              :key="cat.id"
              :to="`/forum/category/${cat.id}`"
              class="flex items-center gap-3 px-4 py-1.5 sidebar-item"
              :class="{ active: currentCategoryId === cat.id }"
              @click="sidebarOpen = false"
            >
              <i :class="categoryIcon(cat.type)" class="text-xs w-4"></i>
              <span>{{ cat.name }}</span>
            </router-link>
          </nav>
        </div>
      </aside>

      <!-- Main Content -->
      <main class="flex-1 min-w-0 p-0 md:p-6">
        <RouterView />
      </main>
    </div>

    <!-- Mobile Bottom Navigation -->
    <nav class="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around items-center py-2 z-50">
      <router-link to="/" class="flex flex-col items-center gap-0.5 flex-1" :class="isActive('/') ? 'text-[#0064FF]' : 'text-gray-400'">
        <i class="fas fa-home text-lg"></i>
        <span class="text-[10px] font-medium">首页</span>
      </router-link>
      <router-link to="/forum" class="flex flex-col items-center gap-0.5 flex-1" :class="isActive('/forum') ? 'text-[#0064FF]' : 'text-gray-400'">
        <i class="fas fa-compass text-lg"></i>
        <span class="text-[10px] font-medium">探索</span>
      </router-link>
      <router-link to="/forum/create" class="flex-1 flex justify-center">
        <div class="bg-[#0064FF] w-12 h-9 rounded flex items-center justify-center shadow-md shadow-blue-200 -mt-3">
          <i class="fas fa-plus text-white text-sm"></i>
        </div>
      </router-link>
      <router-link to="/user/settings" class="flex flex-col items-center gap-0.5 flex-1" :class="isActive('/user') ? 'text-[#0064FF]' : 'text-gray-400'">
        <i class="fas fa-bell text-lg"></i>
        <span class="text-[10px] font-medium">消息</span>
      </router-link>
      <router-link v-if="auth.isAuthenticated" to="/user/settings" class="flex flex-col items-center gap-0.5 flex-1" :class="isActive('/user') ? 'text-[#0064FF]' : 'text-gray-400'">
        <i class="fas fa-user text-lg"></i>
        <span class="text-[10px] font-medium">我的</span>
      </router-link>
      <router-link v-else to="/login" class="flex flex-col items-center gap-0.5 flex-1 text-gray-400">
        <i class="fas fa-user text-lg"></i>
        <span class="text-[10px] font-medium">我的</span>
      </router-link>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { fetchCategories } from '../api/forum'
import type { Category } from '../types/models'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const sidebarOpen = ref(false)
const userMenuOpen = ref(false)
const categories = ref<Category[]>([])

const currentCategoryId = computed(() => {
  const id = route.params.id
  return id ? Number(id) : null
})

const avatarText = computed(() => {
  const name = auth.user?.username || ''
  return name.slice(0, 2).toUpperCase()
})

function isActive(path: string) {
  return route.path.startsWith(path)
}

function categoryIcon(type: string) {
  const icons: Record<string, string> = {
    forum: 'fas fa-fire-alt',
    contest: 'fas fa-trophy',
    recruit_project: 'fas fa-project-diagram',
    recruit_team: 'fas fa-users',
    notice: 'fas fa-bullhorn',
  }
  return icons[type] || 'fas fa-microchip'
}

async function loadCategories() {
  try {
    categories.value = await fetchCategories()
  } catch {
    // ignore
  }
}

async function handleLogout() {
  userMenuOpen.value = false
  await auth.doLogout()
  router.push('/')
}

function closeUserMenu(e: MouseEvent) {
  const target = e.target as Node
  const menuEl = document.querySelector('[ref="userMenuRef"]')
  if (userMenuOpen.value && !menuEl?.contains(target)) {
    userMenuOpen.value = false
  }
}

watch(route, () => {
  sidebarOpen.value = false
})

onMounted(() => {
  loadCategories()
  document.addEventListener('click', closeUserMenu)
})

onUnmounted(() => {
  document.removeEventListener('click', closeUserMenu)
})
</script>