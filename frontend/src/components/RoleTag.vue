<template>
  <el-tag v-if="role" :style="tagStyle" size="small" effect="light">{{ role.display_name }}</el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

import type { User } from '../types/models'

const props = defineProps<{
  user: User
}>()

const role = computed(() =>
  [...props.user.roles].sort((left, right) => right.priority - left.priority)[0],
)

const tagStyle = computed(() => ({
  borderColor: role.value?.color || '#409eff',
  color: role.value?.color || '#409eff',
}))
</script>
