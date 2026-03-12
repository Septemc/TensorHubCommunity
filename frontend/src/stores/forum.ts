import { defineStore } from 'pinia'

import { createComment, createPost, fetchCategories, fetchCategoryPosts, fetchComments, fetchPost, fetchPosts, togglePostLike } from '../api/forum'
import type { Category, Comment, Post } from '../types/models'

export const useForumStore = defineStore('forum', {
  state: () => ({
    categories: [] as Category[],
    posts: [] as Post[],
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
    async loadPost(id: number) {
      this.currentPost = await fetchPost(id)
      this.comments = await fetchComments(id)
      return this.currentPost
    },
    async submitPost(payload: Record<string, unknown>) {
      return createPost(payload)
    },
    async submitComment(postId: number, payload: Record<string, unknown>) {
      const comment = await createComment(postId, payload)
      this.comments.push(comment)
      return comment
    },
    async likePost(postId: number) {
      const data = await togglePostLike(postId)
      if (this.currentPost?.id === postId) {
        this.currentPost.likes_count = data.likes_count
      }
      return data
    },
  },
})
