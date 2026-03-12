import { defineStore } from 'pinia'

import {
  assignRoles,
  createAnnouncement,
  createCategory,
  fetchAdminAnnouncements,
  fetchAdminPosts,
  fetchRoles,
  fetchSitePage,
  fetchUsers,
  togglePostEssence,
  togglePostTop,
  updateAnnouncement,
  updateCategory,
  updateSitePage,
  updateVerification,
} from '../api/admin'
import type { Announcement, Category, Post, SitePage, User } from '../types/models'

export const useAdminStore = defineStore('admin', {
  state: () => ({
    users: [] as User[],
    roles: [] as any[],
    announcements: [] as Announcement[],
    posts: [] as Post[],
    pages: {} as Record<string, SitePage>,
  }),
  actions: {
    async loadUsers() {
      this.users = await fetchUsers()
      return this.users
    },
    async loadRoles() {
      this.roles = await fetchRoles()
      return this.roles
    },
    async setVerification(userId: number, verificationStatus: string) {
      const user = await updateVerification(userId, verificationStatus)
      this.users = this.users.map((item) => (item.id === user.id ? user : item))
      return user
    },
    async setRoles(userId: number, roleIds: number[]) {
      const user = await assignRoles(userId, roleIds)
      this.users = this.users.map((item) => (item.id === user.id ? user : item))
      return user
    },
    async saveCategory(payload: Partial<Category>) {
      if (payload.id) {
        return updateCategory(payload.id, payload)
      }
      return createCategory(payload)
    },
    async loadAnnouncements() {
      this.announcements = await fetchAdminAnnouncements()
      return this.announcements
    },
    async saveAnnouncement(payload: Partial<Announcement>) {
      const result = payload.id ? await updateAnnouncement(payload.id, payload) : await createAnnouncement(payload)
      await this.loadAnnouncements()
      return result
    },
    async loadPage(slug: string) {
      const page = await fetchSitePage(slug)
      this.pages[slug] = page
      return page
    },
    async savePage(slug: string, payload: Partial<SitePage>) {
      const page = await updateSitePage(slug, payload)
      this.pages[slug] = page
      return page
    },
    async loadPosts() {
      this.posts = await fetchAdminPosts()
      return this.posts
    },
    async flipTop(postId: number) {
      await togglePostTop(postId)
      return this.loadPosts()
    },
    async flipEssence(postId: number) {
      await togglePostEssence(postId)
      return this.loadPosts()
    },
  },
})
