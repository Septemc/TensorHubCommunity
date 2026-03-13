<template>
  <nav class="mobile-tabbar">
    <button
      v-for="item in items"
      :key="item.to"
      class="mobile-tabbar__item"
      :class="{ 'is-active': isActive(item) }"
      type="button"
      @click="router.push(item.to)"
    >
      <el-icon class="mobile-tabbar__icon">
        <component :is="icons[item.icon || 'House']" />
      </el-icon>
      <span>{{ item.label }}</span>
    </button>
    <button
      class="mobile-tabbar__item"
      :class="{ 'is-active': route.path.startsWith('/user') || route.path.startsWith('/login') || route.path.startsWith('/register') }"
      type="button"
      @click="router.push(profileTarget)"
    >
      <el-icon class="mobile-tabbar__icon">
        <UserFilled />
      </el-icon>
      <span>{{ auth.user ? '我的' : '登录' }}</span>
    </button>
  </nav>
</template>

<script setup lang="ts">
import { Bell, ChatDotSquare, Compass, House, UserFilled } from '@element-plus/icons-vue'
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { isRouteActive, mobileTabItems } from '../router/navigation'
import { useAuthStore } from '../stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const icons: Record<string, unknown> = {
  Bell,
  ChatDotSquare,
  Compass,
  House,
}

const items = mobileTabItems
const profileTarget = computed(() => (auth.user ? '/user/settings' : '/login'))

function isActive(item: (typeof items)[number]) {
  return isRouteActive(route, item)
}
</script>

<style scoped>
.mobile-tabbar {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: 12px;
  z-index: 45;
  display: none;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 6px;
  padding: 8px;
  border-radius: 22px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(18px);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.18);
  border: 1px solid rgba(148, 163, 184, 0.18);
}

.mobile-tabbar__item {
  border: none;
  background: transparent;
  min-height: 56px;
  border-radius: 16px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  color: #64748b;
  font-size: 11px;
  font-weight: 700;
}

.mobile-tabbar__item.is-active {
  background: #eff6ff;
  color: #2563eb;
}

.mobile-tabbar__icon {
  font-size: 18px;
}

@media (max-width: 960px) {
  .mobile-tabbar {
    display: grid;
  }
}
</style>