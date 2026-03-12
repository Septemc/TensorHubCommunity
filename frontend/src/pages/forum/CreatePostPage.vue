<template>
  <el-card>
    <template #header>
      <div class="section-title"><span>发布帖子</span></div>
    </template>
    <el-alert
      v-if="auth.user?.verification_status !== 'approved'"
      title="当前账号尚未审核通过，暂时不能发帖。"
      type="warning"
      show-icon
      :closable="false"
    />
    <el-form label-position="top" :model="form">
      <el-form-item label="板块">
        <el-select v-model="form.category_id" style="width: 100%">
          <el-option v-for="item in forum.categories" :key="item.id" :label="item.name" :value="item.id" />
        </el-select>
      </el-form-item>
      <el-form-item label="标题">
        <el-input v-model="form.title" />
      </el-form-item>
      <el-form-item label="帖子类型">
        <el-select v-model="form.post_type" style="width: 100%">
          <el-option label="普通帖" value="general" />
          <el-option label="竞赛讯息" value="contest" />
          <el-option label="项目招募" value="recruit_project" />
          <el-option label="组队招募" value="recruit_team" />
        </el-select>
      </el-form-item>
      <el-form-item label="内容 Markdown">
        <el-input v-model="form.content" type="textarea" :rows="14" />
      </el-form-item>
      <el-form-item label="结构化附加信息 JSON">
        <el-input v-model="extraDataText" type="textarea" :rows="5" />
      </el-form-item>
      <el-button type="primary" :disabled="!auth.isVerified" @click="submit">提交</el-button>
    </el-form>
  </el-card>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useRouter } from 'vue-router'

import { useAuthStore } from '../../stores/auth'
import { useForumStore } from '../../stores/forum'

const auth = useAuthStore()
const forum = useForumStore()
const router = useRouter()

const form = reactive({
  title: '',
  content: '',
  category_id: undefined as number | undefined,
  post_type: 'general',
})

const extraDataText = ref('')

async function submit() {
  let extraData = undefined
  if (extraDataText.value.trim()) {
    try {
      extraData = JSON.parse(extraDataText.value)
    } catch {
      ElMessage.error('附加信息必须是合法 JSON')
      return
    }
  }

  const post = await forum.submitPost({ ...form, extra_data: extraData })
  ElMessage.success('帖子发布成功')
  router.push(`/forum/post/${post.id}`)
}

onMounted(() => {
  forum.loadCategories()
})
</script>
