<template>
  <div class="app-shell">
    <AppHeader />
    <main class="app-shell__main">
      <div class="page-shell">
        <RouterView />
      </div>
    </main>
    <MobileTabBar />
  </div>
</template>

<script setup lang="ts">
import AppHeader from '../components/AppHeader.vue'
import MobileTabBar from '../components/MobileTabBar.vue'
</script>
