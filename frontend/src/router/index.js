import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    component: () => import('../components/Layout.vue'),
    children: [
      {
        path: '/',
        name: 'home',
        component: () => import('../views/Home.vue')
      },
      {
        path: '/rental',
        name: 'rental',
        children: [
          {
            path: '',
            name: 'rental-list',
            component: () => import('../views/rental/RentalList.vue')
          },
          {
            path: 'publish',
            name: 'rental-publish',
            component: () => import('../views/rental/RentalPublish.vue')
          },
          {
            path: ':id',
            name: 'rental-detail',
            component: () => import('../views/rental/RentalDetail.vue')
          }
        ]
      },
      {
        path: '/trade',
        name: 'trade',
        children: [
          {
            path: '',
            name: 'trade-list',
            component: () => import('../views/trade/TradeList.vue')
          },
          {
            path: 'publish',
            name: 'trade-publish',
            component: () => import('../views/trade/TradePublish.vue')
          },
          {
            path: ':id',
            name: 'trade-detail',
            component: () => import('../views/trade/TradeDetail.vue')
          }
        ]
      },
      {
        path: '/user',
        name: 'user',
        children: [
          {
            path: 'profile',
            name: 'user-profile',
            component: () => import('../views/user/Profile.vue')
          },
          {
            path: 'my-items',
            name: 'my-items',
            component: () => import('../views/user/MyItems.vue')
          },
          {
            path: 'orders',
            name: 'my-orders',
            component: () => import('../views/user/MyOrders.vue')
          }
        ]
      }
    ]
  },
  {
    path: '/user/login',
    name: 'login',
    component: () => import('../views/user/Login.vue')
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

export default router
