export interface Role {
  id: number
  name: string
  display_name: string
  color?: string | null
  priority: number
}

export interface User {
  id: number
  username: string
  email?: string | null
  real_name?: string
  gender?: string
  major?: string
  student_id?: string
  avatar?: string | null
  status?: number
  verification_status: 'pending' | 'approved' | 'rejected'
  roles: Role[]
  created_at?: string
  updated_at?: string | null
}

export interface Category {
  id: number
  name: string
  description?: string | null
  parent_id?: number | null
  type: string
  sort_order: number
  is_active: boolean
  posts_count: number
}

export interface Post {
  id: number
  title: string
  content: string
  user_id: number
  category_id: number
  post_type: string
  extra_data?: Record<string, unknown> | null
  views: number
  likes_count: number
  comments_count: number
  is_top: boolean
  is_essence: boolean
  is_liked?: boolean
  status: number
  created_at?: string
  updated_at?: string | null
  author: User
}

export interface Comment {
  id: number
  content: string
  user_id: number
  post_id: number
  parent_id?: number | null
  likes_count: number
  created_at?: string
  updated_at?: string | null
  author: User
}

export interface Announcement {
  id: number
  title: string
  content: string
  cover_image?: string | null
  is_published: boolean
  created_at?: string
  updated_at?: string | null
  author?: User | null
}

export interface SitePage {
  id: number
  slug: string
  title: string
  content: string
  is_published: boolean
  created_at?: string
  updated_at?: string | null
}