import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '../layouts/MainLayout.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: MainLayout,
      children: [
        { path: '', component: () => import('../pages/site/HomePage.vue') },
        { path: 'about', component: () => import('../pages/site/AboutPage.vue') },
        { path: 'news', component: () => import('../pages/site/NewsListPage.vue') },
        { path: 'news/:id', component: () => import('../pages/site/NewsDetailPage.vue') },
        { path: 'forum', component: () => import('../pages/forum/ForumHomePage.vue') },
        { path: 'forum/category/:id', component: () => import('../pages/forum/CategoryPage.vue') },
        { path: 'forum/post/:id', component: () => import('../pages/forum/PostDetailPage.vue') },
        { path: 'forum/post/:id/edit', component: () => import('../pages/forum/CreatePostPage.vue'), meta: { requiresAuth: true, requiresVerified: true } },
        { path: 'forum/create', component: () => import('../pages/forum/CreatePostPage.vue'), meta: { requiresAuth: true, requiresVerified: true } },
        { path: 'user/settings', component: () => import('../pages/user/UserSettingsPage.vue'), meta: { requiresAuth: true } },
        { path: 'login', component: () => import('../pages/user/LoginPage.vue'), meta: { guestOnly: true } },
        { path: 'register', component: () => import('../pages/user/RegisterPage.vue'), meta: { guestOnly: true } },
        { path: 'admin', component: () => import('../pages/admin/AdminDashboardPage.vue'), meta: { requiresAuth: true, requiresAdmin: true } },
      ],
    },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  await auth.initialize()

  if (to.meta.guestOnly && auth.isAuthenticated) {
    return '/'
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return '/login'
  }

  if (to.meta.requiresVerified && !auth.isVerified) {
    return '/user/settings'
  }

  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return '/'
  }

  return true
})

export default router
