<template>
  <el-container>
    <AppHeader />
    <el-main>
      <div class="page-shell">
        <RouterView />
      </div>
    </el-main>
  </el-container>
</template>

<script setup lang="ts">
import AppHeader from '../components/AppHeader.vue'
</script>
