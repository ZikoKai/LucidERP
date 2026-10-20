import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import Orders from './views/Orders.vue'
import OrderDetail from './views/OrderDetail.vue'
import Proposals from './views/Proposals.vue'
import './style.css'

const router = createRouter({ history: createWebHistory(), routes: [
  { path: '/', component: Orders },
  { path: '/orders/:id', component: OrderDetail },
  { path: '/proposals', component: Proposals },
] })
createApp(App).use(router).mount('#app')
