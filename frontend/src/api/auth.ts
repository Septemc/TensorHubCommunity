import api from './client'
import type { User } from '../types/models'

export interface RegisterPayload {
  username: string
  password: string
  email?: string
  real_name: string
  gender: string
  major: string
  student_id: string
}

export interface LoginPayload {
  identifier: string
  password: string
}

export async function register(payload: RegisterPayload) {
  const { data } = await api.post<User>('/auth/register', payload)
  return data
}

export async function login(payload: LoginPayload) {
  const { data } = await api.post<{ user: User; csrf_token: string }>('/auth/login', payload)
  return data
}

export async function logout() {
  const { data } = await api.post<{ message: string }>('/auth/logout')
  return data
}

export async function fetchProfile() {
  const { data } = await api.get<User>('/auth/profile')
  return data
}

export async function updateProfile(payload: Partial<User>) {
  const { data } = await api.put<User>('/auth/profile', payload)
  return data
}
