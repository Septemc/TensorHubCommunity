<template>
  <el-row justify="center">
    <el-col :span="14">
      <el-card>
        <template #header><div class="section-title"><span>实名注册</span></div></template>
        <el-form label-position="top" :model="form">
          <div class="card-grid two">
            <el-form-item label="用户名"><el-input v-model="form.username" /></el-form-item>
            <el-form-item label="邮箱"><el-input v-model="form.email" /></el-form-item>
            <el-form-item label="真实姓名"><el-input v-model="form.real_name" /></el-form-item>
            <el-form-item label="性别"><el-input v-model="form.gender" /></el-form-item>
            <el-form-item label="专业"><el-input v-model="form.major" /></el-form-item>
            <el-form-item label="学号"><el-input v-model="form.student_id" /></el-form-item>
            <el-form-item label="密码"><el-input v-model="form.password" type="password" show-password /></el-form-item>
          </div>
          <el-button type="primary" @click="submit">提交注册</el-button>
        </el-form>
      </el-card>
    </el-col>
  </el-row>
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = reactive({
  username: '',
  password: '',
  email: '',
  real_name: '',
  gender: 'other',
  major: '',
  student_id: '',
})

async function submit() {
  await auth.doRegister(form)
  ElMessage.success('注册成功，请等待管理员审核')
  router.push('/login')
}
</script>