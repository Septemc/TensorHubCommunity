import api from './client'
import type { Announcement, Category, Post, SitePage, User } from '../types/models'

export async function fetchUsers() {
  const { data } = await api.get<User[]>('/admin/users')
  return data
}

export async function fetchRoles() {
  const { data } = await api.get('/admin/roles')
  return data
}

export async function updateVerification(userId: number, verification_status: string) {
  const { data } = await api.put<User>(`/auth/users/${userId}/verification`, { verification_status })
  return data
}

export async function assignRoles(userId: number, roleIds: number[]) {
  const { data } = await api.put<User>(`/auth/users/${userId}/roles`, { role_ids: roleIds })
  return data
}

export async function createCategory(payload: Partial<Category>) {
  const { data } = await api.post<Category>('/admin/categories', payload)
  return data
}

export async function updateCategory(categoryId: number, payload: Partial<Category>) {
  const { data } = await api.put<Category>(`/admin/categories/${categoryId}`, payload)
  return data
}

export async function fetchAdminAnnouncements() {
  const { data } = await api.get<Announcement[]>('/admin/announcements')
  return data
}

export async function createAnnouncement(payload: Partial<Announcement>) {
  const { data } = await api.post<Announcement>('/admin/announcements', payload)
  return data
}

export async function updateAnnouncement(id: number, payload: Partial<Announcement>) {
  const { data } = await api.put<Announcement>(`/admin/announcements/${id}`, payload)
  return data
}

export async function fetchSitePage(slug: string) {
  const { data } = await api.get<SitePage>(`/admin/site/pages/${slug}`)
  return data
}

export async function updateSitePage(slug: string, payload: Partial<SitePage>) {
  const { data } = await api.put<SitePage>(`/admin/site/pages/${slug}`, payload)
  return data
}

export async function fetchAdminPosts() {
  const { data } = await api.get<Post[]>('/admin/posts')
  return data
}

export async function togglePostTop(postId: number) {
  const { data } = await api.put<Post>(`/admin/posts/${postId}/top`)
  return data
}

export async function togglePostEssence(postId: number) {
  const { data } = await api.put<Post>(`/admin/posts/${postId}/essence`)
  return data
}

export async function uploadImage(file: File) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post<{ url: string }>('/uploads/image', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}
