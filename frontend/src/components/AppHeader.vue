<template>
  <el-header class="header-wrap">
    <div class="header-inner">
      <RouterLink to="/" class="brand">TensorHub</RouterLink>
      <el-menu mode="horizontal" :ellipsis="false" :default-active="route.path" router>
        <el-menu-item index="/">首页</el-menu-item>
        <el-menu-item index="/about">团队介绍</el-menu-item>
        <el-menu-item index="/news">官方讯息</el-menu-item>
        <el-menu-item index="/forum">论坛</el-menu-item>
        <el-menu-item index="/forum/create">发帖</el-menu-item>
        <el-menu-item index="/admin" v-if="auth.isAdmin">后台</el-menu-item>
      </el-menu>
      <div class="header-actions">
        <template v-if="auth.user">
          <RoleTag :user="auth.user" />
          <span>{{ auth.user.username }}</span>
          <el-button link @click="router.push('/user/settings')">个人中心</el-button>
          <el-button link @click="onLogout">退出</el-button>
        </template>
        <template v-else>
          <el-button link @click="router.push('/login')">登录</el-button>
          <el-button type="primary" @click="router.push('/register')">注册</el-button>
        </template>
      </div>
    </div>
  </el-header>
</template>

<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'

import { useAuthStore } from '../stores/auth'
import RoleTag from './RoleTag.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

async function onLogout() {
  await auth.doLogout()
  router.push('/')
}
</script>

<style scoped>
.header-wrap {
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  position: sticky;
  top: 0;
  z-index: 20;
}

.header-inner {
  max-width: 1200px;
  height: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.brand {
  font-weight: 700;
  font-size: 20px;
  color: #409eff;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
</style>
