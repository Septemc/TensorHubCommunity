import api from './client'
import type { Category, Comment, Post } from '../types/models'

export async function fetchCategories() {
  const { data } = await api.get<Category[]>('/categories')
  return data
}

export async function fetchPosts(sort = 'latest') {
  const { data } = await api.get<Post[]>('/posts', { params: { sort } })
  return data
}

export async function fetchCategoryPosts(categoryId: number, sort = 'latest') {
  const { data } = await api.get<Post[]>(`/categories/${categoryId}/posts`, { params: { sort } })
  return data
}

export async function fetchPost(id: number) {
  const { data } = await api.get<Post>(`/posts/${id}`)
  return data
}

export async function fetchComments(postId: number) {
  const { data } = await api.get<Comment[]>(`/posts/${postId}/comments`)
  return data
}

export async function createPost(payload: Record<string, unknown>) {
  const { data } = await api.post<Post>('/posts', payload)
  return data
}

export async function createComment(postId: number, payload: Record<string, unknown>) {
  const { data } = await api.post<Comment>(`/posts/${postId}/comments`, payload)
  return data
}

export async function togglePostLike(postId: number) {
  const { data } = await api.post<{ liked: boolean; likes_count: number }>(`/posts/${postId}/like`)
  return data
}
