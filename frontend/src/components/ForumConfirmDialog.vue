<template>
  <transition name="forum-confirm-fade">
    <div v-if="modelValue" class="forum-confirm" @click.self="cancel">
      <div class="forum-confirm__panel">
        <div class="forum-confirm__badge">确认操作</div>
        <h3>{{ title }}</h3>
        <p>{{ message }}</p>
        <div class="forum-confirm__actions">
          <button type="button" class="forum-confirm__button forum-confirm__button--ghost" @click="cancel">
            取消
          </button>
          <button type="button" class="forum-confirm__button forum-confirm__button--danger" @click="confirm">
            {{ confirmText }}
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    modelValue: boolean
    title?: string
    message: string
    confirmText?: string
  }>(),
  {
    title: '确认操作',
    confirmText: '确认',
  },
)

const emit = defineEmits<{
  'update:modelValue': [boolean]
  confirm: []
  cancel: []
}>()

function cancel() {
  emit('update:modelValue', false)
  emit('cancel')
}

function confirm() {
  emit('confirm')
  emit('update:modelValue', false)
}
</script>

<style scoped>
.forum-confirm {
  position: fixed;
  inset: 0;
  z-index: 120;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(15, 23, 42, 0.42);
  backdrop-filter: blur(8px);
}

.forum-confirm__panel {
  width: min(100%, 420px);
  padding: 28px;
  border-radius: 28px;
  background: linear-gradient(180deg, #ffffff, #f8fafc);
  box-shadow: 0 24px 80px rgba(15, 23, 42, 0.22);
}

.forum-confirm__badge {
  display: inline-flex;
  min-height: 30px;
  align-items: center;
  padding: 0 12px;
  border-radius: 999px;
  background: #eff6ff;
  color: #2563eb;
  font-size: 12px;
  font-weight: 700;
}

.forum-confirm__panel h3 {
  margin: 16px 0 10px;
  font-size: 24px;
  color: #0f172a;
}

.forum-confirm__panel p {
  margin: 0;
  color: #475569;
  line-height: 1.7;
}

.forum-confirm__actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
}

.forum-confirm__button {
  min-width: 96px;
  min-height: 44px;
  padding: 0 18px;
  border-radius: 14px;
  border: none;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
}

.forum-confirm__button--ghost {
  background: #e2e8f0;
  color: #334155;
}

.forum-confirm__button--danger {
  background: #ef4444;
  color: #fff;
}

.forum-confirm-fade-enter-active,
.forum-confirm-fade-leave-active {
  transition: opacity 0.2s ease;
}

.forum-confirm-fade-enter-from,
.forum-confirm-fade-leave-to {
  opacity: 0;
}
</style>