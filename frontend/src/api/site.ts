import api from './client'
import type { Announcement, SitePage } from '../types/models'

export async function fetchHome() {
  const { data } = await api.get<{
    page: SitePage | null
    announcements: Announcement[]
    hot_posts: any[]
    stats: Record<string, number>
  }>('/site/home')
  return data
}

export async function fetchPage(slug: string) {
  const { data } = await api.get<SitePage>(`/site/pages/${slug}`)
  return data
}

export async function fetchAnnouncements() {
  const { data } = await api.get<Announcement[]>('/site/announcements')
  return data
}

export async function fetchAnnouncement(id: number) {
  const { data } = await api.get<Announcement>(`/site/announcements/${id}`)
  return data
}
