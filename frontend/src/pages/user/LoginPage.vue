<template>
  <el-row justify="center">
    <el-col :span="10">
      <el-card>
        <template #header><div class="section-title"><span>登录</span></div></template>
        <el-form label-position="top" :model="form" @submit.prevent="submit">
          <el-form-item label="用户名或邮箱">
            <el-input v-model="form.identifier" />
          </el-form-item>
          <el-form-item label="密码">
            <el-input v-model="form.password" type="password" show-password />
          </el-form-item>
          <el-button type="primary" @click="submit">登录</el-button>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = reactive({ identifier: '', password: '' })

async function submit() {
  try {
    await auth.doLogin(form)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (error) {
    const message = axios.isAxiosError(error)
      ? (error.response?.data?.detail ?? '登录失败，请检查后端与数据库配置')
      : '登录失败，请稍后重试'
    ElMessage.error(message)
  }
}
</script>
