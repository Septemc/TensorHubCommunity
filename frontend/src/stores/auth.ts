import { defineStore } from 'pinia'

import { fetchProfile, login, logout, register, updateProfile } from '../api/auth'
import type { RegisterPayload } from '../api/auth'
import type { User } from '../types/models'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    loading: false,
    initialized: false,
  }),
  getters: {
    isAuthenticated: (state) => Boolean(state.user),
    isAdmin: (state) => Boolean(state.user?.roles.some((role) => role.name === 'admin')),
    isVerified: (state) => state.user?.verification_status === 'approved',
  },
  actions: {
    async initialize() {
      if (this.initialized) return
      try {
        this.loading = true
        this.user = await fetchProfile()
      } catch {
        this.user = null
      } finally {
        this.initialized = true
        this.loading = false
      }
    },
    async doLogin(payload: { identifier: string; password: string }) {
      const response = await login(payload)
      this.user = response.user
      this.initialized = true
      return response
    },
    async doRegister(payload: RegisterPayload) {
      return register(payload)
    },
    async doLogout() {
      await logout()
      this.user = null
    },
    async saveProfile(payload: Partial<User>) {
      this.user = await updateProfile(payload)
      return this.user
    },
  },
})
