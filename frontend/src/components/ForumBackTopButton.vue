<template>
  <transition name="forum-back-top-fade">
    <button v-if="visible" type="button" class="forum-back-top" @click="scrollToTop">
      <span class="forum-back-top__icon">↑</span>
      <span>回顶层</span>
    </button>
  </transition>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'

const visible = ref(false)

function updateVisible() {
  visible.value = window.scrollY > 280
}

function scrollToTop() {
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

onMounted(() => {
  updateVisible()
  window.addEventListener('scroll', updateVisible, { passive: true })
})

onBeforeUnmount(() => {
  window.removeEventListener('scroll', updateVisible)
})
</script>

<style scoped>
.forum-back-top {
  position: fixed;
  top: 92px;
  right: max(20px, calc((100vw - 1200px) / 2 + 20px));
  z-index: 34;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 40px;
  padding: 0 14px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.96);
  box-shadow: 0 14px 28px rgba(15, 23, 42, 0.08);
  color: #334155;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  backdrop-filter: blur(14px);
}

.forum-back-top:hover {
  color: #2563eb;
  border-color: rgba(59, 130, 246, 0.24);
}

.forum-back-top__icon {
  font-size: 14px;
  line-height: 1;
}

.forum-back-top-fade-enter-active,
.forum-back-top-fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.forum-back-top-fade-enter-from,
.forum-back-top-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

@media (max-width: 960px) {
  .forum-back-top {
    top: 78px;
    right: 16px;
  }
}
</style>