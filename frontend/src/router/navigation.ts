import type { RouteLocationNormalizedLoaded } from 'vue-router'

export interface NavItem {
  label: string
  to: string
  icon?: string
  match?: (path: string) => boolean
}

export const primaryNavItems: NavItem[] = [
  { label: '首页', to: '/', icon: 'House', match: (path) => path === '/' },
  { label: '官方讯息', to: '/news', icon: 'Bell', match: (path) => path.startsWith('/news') },
  { label: '论坛', to: '/forum', icon: 'ChatDotSquare', match: (path) => path.startsWith('/forum') },
  { label: '关于我们', to: '/about', icon: 'Compass', match: (path) => path.startsWith('/about') },
]

export const mobileTabItems: NavItem[] = [
  { label: '首页', to: '/', icon: 'House', match: (path) => path === '/' },
  { label: '资讯', to: '/news', icon: 'Bell', match: (path) => path.startsWith('/news') },
  { label: '论坛', to: '/forum', icon: 'ChatDotSquare', match: (path) => path.startsWith('/forum') },
  { label: '关于', to: '/about', icon: 'Compass', match: (path) => path.startsWith('/about') },
]

export function isRouteActive(route: RouteLocationNormalizedLoaded, item: NavItem): boolean {
  return item.match ? item.match(route.path) : route.path === item.to
}