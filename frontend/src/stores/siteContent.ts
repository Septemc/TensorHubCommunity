import { defineStore } from 'pinia'

import { fetchAnnouncement, fetchAnnouncements, fetchHome, fetchPage } from '../api/site'
import type { Announcement, Post, SitePage } from '../types/models'

export const useSiteContentStore = defineStore('siteContent', {
  state: () => ({
    homePage: null as SitePage | null,
    announcements: [] as Announcement[],
    hotPosts: [] as Post[],
    stats: {} as Record<string, number>,
    pages: {} as Record<string, SitePage>,
  }),
  actions: {
    async loadHome() {
      const data = await fetchHome()
      this.homePage = data.page
      this.announcements = data.announcements
      this.hotPosts = data.hot_posts
      this.stats = data.stats
      return data
    },
    async loadPage(slug: string) {
      const page = await fetchPage(slug)
      this.pages[slug] = page
      return page
    },
    async loadAnnouncements() {
      this.announcements = await fetchAnnouncements()
      return this.announcements
    },
    async loadAnnouncement(id: number) {
      return fetchAnnouncement(id)
    },
  },
})
