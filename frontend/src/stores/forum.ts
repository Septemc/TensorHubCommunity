import { defineStore } from 'pinia'

import {
  createComment,
  createPost,
  deletePost as destroyPost,
  fetchCategories,
  fetchCategoryPosts,
  fetchComments,
  fetchPost,
  fetchPosts,
  fetchUserPosts,
  togglePostLike,
  updatePost,
} from '../api/forum'
import type { Category, Comment, Post } from '../types/models'

function syncPostList(posts: Post[], post: Post) {
  return posts.map((item) => (item.id === post.id ? post : item))
}

export const useForumStore = defineStore('forum', {
  state: () => ({
    categories: [] as Category[],
    posts: [] as Post[],
    userPosts: [] as Post[],
    currentPost: null as Post | null,
    comments: [] as Comment[],
  }),
  actions: {
    async loadCategories() {
      this.categories = await fetchCategories()
      return this.categories
    },
    async loadPosts(sort = 'latest') {
      this.posts = await fetchPosts(sort)
      return this.posts
    },
    async loadCategoryPosts(categoryId: number, sort = 'latest') {
      this.posts = await fetchCategoryPosts(categoryId, sort)
      return this.posts
    },
    async loadUserPosts(userId: number) {
      this.userPosts = await fetchUserPosts(userId)
      return this.userPosts
    },
    async loadPost(id: number) {
      this.currentPost = await fetchPost(id)
      this.comments = await fetchComments(id)
      return this.currentPost
    },
    async submitPost(payload: Record<string, unknown>) {
      const post = await createPost(payload)
      this.currentPost = post
      this.userPosts.unshift(post)
      return post
    },
    async savePost(postId: number, payload: Record<string, unknown>) {
      const post = await updatePost(postId, payload)
      this.currentPost = post
      this.posts = syncPostList(this.posts, post)
      this.userPosts = syncPostList(this.userPosts, post)
      return post
    },
    async removePost(postId: number) {
      const result = await destroyPost(postId)
      this.posts = this.posts.filter((item) => item.id !== postId)
      this.userPosts = this.userPosts.filter((item) => item.id !== postId)
      if (this.currentPost?.id === postId) {
        this.currentPost = null
      }
      return result
    },
    async submitComment(postId: number, payload: Record<string, unknown>) {
      const comment = await createComment(postId, payload)
      this.comments.push(comment)
      if (this.currentPost?.id === postId) {
        this.currentPost.comments_count += 1
      }
      return comment
    },
    async likePost(postId: number) {
      const data = await togglePostLike(postId)
      if (this.currentPost?.id === postId) {
        this.currentPost.likes_count = data.likes_count
      }
      this.posts = this.posts.map((item) => (item.id === postId ? { ...item, likes_count: data.likes_count } : item))
      this.userPosts = this.userPosts.map((item) => (item.id === postId ? { ...item, likes_count: data.likes_count } : item))
      return data
    },
  },
})
