<template>
  <header class="app-header">
    <div class="app-header__inner">
      <div class="app-header__left">
        <RouterLink to="/" class="app-header__brand">
          <img :src="brandIcon" alt="TensorHub" class="app-header__brand-icon" />
          <div class="app-header__brand-copy">
            <span class="app-header__brand-mark">TensorHub</span>
            <span class="app-header__brand-sub">技术社区</span>
          </div>
        </RouterLink>

        <nav class="app-header__nav desktop-only">
          <button
            v-for="item in primaryNavItems"
            :key="item.to"
            type="button"
            class="app-header__nav-item"
            :class="{ 'is-active': isActive(item) }"
            @click="router.push(item.to)"
          >
            {{ item.label }}
          </button>
        </nav>
      </div>

      <div class="app-header__right desktop-only">
        <el-button v-if="auth.isVerified" type="primary" plain @click="router.push('/forum/create')">发帖</el-button>
        <template v-if="auth.user">
          <RoleTag :user="auth.user" />
          <el-dropdown trigger="click">
            <button class="app-header__user-trigger" type="button">
              <span>{{ auth.user.username }}</span>
              <el-icon><ArrowDown /></el-icon>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/user/settings')">个人中心</el-dropdown-item>
                <el-dropdown-item divided @click="onLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button link @click="router.push('/login')">登录</el-button>
          <el-button type="primary" @click="router.push('/register')">注册</el-button>
        </template>
      </div>

      <div class="app-header__mobile mobile-only">
        <el-button
          v-if="auth.user"
          class="app-header__mobile-user"
          text
          @click="router.push('/user/settings')"
        >
          {{ auth.user.username }}
        </el-button>
        <el-button v-else text @click="router.push('/login')">登录</el-button>
        <el-button circle @click="drawerVisible = true">
          <el-icon><Expand /></el-icon>
        </el-button>
      </div>
    </div>
  </header>

  <el-drawer v-model="drawerVisible" direction="rtl" size="84%" :with-header="false">
    <div class="mobile-drawer">
      <div class="mobile-drawer__profile">
        <div class="mobile-drawer__brand">
          <img :src="brandIcon" alt="TensorHub" class="mobile-drawer__brand-icon" />
          <div>
            <div class="mobile-drawer__title">TensorHub</div>
            <div class="mobile-drawer__subtitle">高校技术交流社区</div>
          </div>
        </div>
        <RoleTag v-if="auth.user" :user="auth.user" />
      </div>

      <div class="mobile-drawer__nav">
        <button
          v-for="item in drawerNavItems"
          :key="item.to"
          type="button"
          class="mobile-drawer__nav-item"
          :class="{ 'is-active': isActive(item) }"
          @click="navigate(item.to)"
        >
          {{ item.label }}
        </button>
      </div>

      <div class="mobile-drawer__actions">
        <template v-if="auth.user">
          <el-button size="large" @click="navigate('/user/settings')">个人中心</el-button>
          <el-button v-if="auth.isVerified" type="primary" plain size="large" @click="navigate('/forum/create')">发布帖子</el-button>
          <el-button type="danger" plain size="large" @click="onLogout">退出登录</el-button>
        </template>
        <template v-else>
          <el-button size="large" @click="navigate('/login')">登录</el-button>
          <el-button type="primary" size="large" @click="navigate('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </el-drawer>
</template>

<script setup lang="ts">
import { ArrowDown, Expand } from '@element-plus/icons-vue'
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import brandIcon from '../assets/tensorhub_icon.png'
import { isRouteActive, primaryNavItems } from '../router/navigation'
import type { NavItem } from '../router/navigation'
import { useAuthStore } from '../stores/auth'
import RoleTag from './RoleTag.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const drawerVisible = ref(false)

const drawerNavItems: NavItem[] = [...primaryNavItems]

function isActive(item: NavItem) {
  return isRouteActive(route, item)
}

function navigate(target: string) {
  drawerVisible.value = false
  router.push(target)
}

async function onLogout() {
  await auth.doLogout()
  drawerVisible.value = false
  router.push('/')
}
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: 40;
  backdrop-filter: blur(20px);
  background: rgba(255, 255, 255, 0.88);
  border-bottom: 1px solid rgba(15, 23, 42, 0.08);
}

.app-header__inner {
  max-width: 1200px;
  margin: 0 auto;
  min-height: 76px;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
}

.app-header__left,
.app-header__right,
.app-header__mobile {
  display: flex;
  align-items: center;
  gap: 14px;
}

.app-header__left {
  min-width: 0;
}

.app-header__brand {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  flex-shrink: 0;
}

.app-header__brand-icon {
  width: 46px;
  height: 46px;
  object-fit: contain;
  border-radius: 14px;
  box-shadow: 0 10px 24px rgba(59, 130, 246, 0.14);
}

.app-header__brand-copy {
  display: flex;
  flex-direction: column;
  gap: 3px;
}

.app-header__brand-mark {
  font-size: 30px;
  line-height: 1;
  font-weight: 800;
  color: #2563eb;
}

.app-header__brand-sub {
  font-size: 12px;
  color: #64748b;
}

.app-header__nav {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-left: 8px;
}

.app-header__nav-item,
.mobile-drawer__nav-item,
.app-header__user-trigger {
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.app-header__nav-item {
  height: 42px;
  padding: 0 16px;
  border-radius: 12px;
  color: #475569;
  font-size: 15px;
  font-weight: 700;
}

.app-header__nav-item:hover,
.app-header__nav-item.is-active {
  background: #eff6ff;
  color: #2563eb;
}

.app-header__user-trigger {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 12px;
  color: #0f172a;
  font-size: 14px;
  font-weight: 600;
}

.app-header__user-trigger:hover {
  background: #f8fafc;
}

.app-header__mobile {
  display: none;
}

.app-header__mobile-user {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mobile-drawer {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.mobile-drawer__profile {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 4px 4px 12px;
}

.mobile-drawer__brand {
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-drawer__brand-icon {
  width: 46px;
  height: 46px;
  object-fit: contain;
}

.mobile-drawer__title {
  font-size: 24px;
  font-weight: 800;
  color: #0f172a;
}

.mobile-drawer__subtitle {
  margin-top: 6px;
  color: #64748b;
  font-size: 13px;
}

.mobile-drawer__nav {
  display: grid;
  gap: 10px;
}

.mobile-drawer__nav-item {
  min-height: 48px;
  padding: 0 16px;
  border-radius: 16px;
  text-align: left;
  font-size: 15px;
  font-weight: 600;
  color: #334155;
  background: #f8fafc;
}

.mobile-drawer__nav-item.is-active {
  background: #eff6ff;
  color: #2563eb;
}

.mobile-drawer__actions {
  display: grid;
  gap: 12px;
}

@media (max-width: 960px) {
  .app-header__inner {
    min-height: 66px;
    padding: 0 16px;
  }

  .app-header__brand-icon {
    width: 38px;
    height: 38px;
  }

  .app-header__brand-mark {
    font-size: 22px;
  }

  .app-header__mobile {
    display: flex;
  }
}
</style>