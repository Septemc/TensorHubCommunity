<template>
  <div class="card-grid two">
    <el-card>
      <template #header><div class="section-title"><span>个人资料</span></div></template>
      <el-descriptions :column="1" border v-if="auth.user">
        <el-descriptions-item label="用户名">{{ auth.user.username }}</el-descriptions-item>
        <el-descriptions-item label="实名">{{ auth.user.real_name }}</el-descriptions-item>
        <el-descriptions-item label="状态">{{ auth.user.verification_status }}</el-descriptions-item>
        <el-descriptions-item label="专业">{{ auth.user.major }}</el-descriptions-item>
        <el-descriptions-item label="学号">{{ auth.user.student_id }}</el-descriptions-item>
      </el-descriptions>
      <el-alert
        v-if="auth.user?.verification_status !== 'approved'"
        title="账号待审核，通过前可登录和完善资料，但不能发帖。"
        type="warning"
        :closable="false"
        show-icon
      />
    </el-card>

    <el-card>
      <template #header><div class="section-title"><span>更新资料</span></div></template>
      <el-form label-position="top" :model="form">
        <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
        <el-form-item label="专业"><el-input v-model="form.major" /></el-form-item>
        <el-form-item label="性别"><el-input v-model="form.gender" /></el-form-item>
        <el-form-item label="真实姓名"><el-input v-model="form.real_name" /></el-form-item>
        <el-form-item label="头像上传">
          <input type="file" accept="image/*" @change="onFileChange" />
        </el-form-item>
        <el-button type="primary" @click="submit">保存</el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { reactive, watchEffect } from 'vue'
import { ElMessage } from 'element-plus'

import { uploadImage } from '../../api/admin'
import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const form = reactive({
  email: '',
  major: '',
  gender: '',
  real_name: '',
  avatar: '',
})

watchEffect(() => {
  form.email = auth.user?.email || ''
  form.major = auth.user?.major || ''
  form.gender = auth.user?.gender || ''
  form.real_name = auth.user?.real_name || ''
  form.avatar = auth.user?.avatar || ''
})

async function onFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  const result = await uploadImage(file)
  form.avatar = result.url
}

async function submit() {
  await auth.saveProfile(form)
  ElMessage.success('资料已更新')
}
</script>
