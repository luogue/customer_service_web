import { createRouter, createWebHistory } from 'vue-router'
import LoginComponent from '../components/LoginComponent.vue'
import ChatView from '../views/ChatView.vue'
import AdminLayout from '../views/admin/AdminLayout.vue'
import ModelConfig from '../views/admin/ModelConfig.vue'
import PromptTemplate from '../views/admin/PromptTemplate.vue'
import FAQManage from '../views/admin/FAQManage.vue'
import ChatRules from '../views/admin/ChatRules.vue'
import TransferConfig from '../views/admin/TransferConfig.vue'
import KnowledgeBase from '../views/admin/KnowledgeBase.vue'
import ScriptConfig from '../views/admin/ScriptConfig.vue'
import AccountManage from '../views/admin/AccountManage.vue'

const routes = [
  {
    path: '/',
    name: 'login',
    component: LoginComponent
  },
  {
    path: '/chat',
    name: 'chat',
    component: ChatView
  },
  {
    path: '/admin',
    name: 'admin',
    component: AdminLayout,
    children: [
      {
        path: 'model',
        name: 'admin-model',
        component: ModelConfig
      },
      {
        path: 'prompt',
        name: 'admin-prompt',
        component: PromptTemplate
      },
      {
        path: 'faq',
        name: 'admin-faq',
        component: FAQManage
      },
      {
        path: 'rules',
        name: 'admin-rules',
        component: ChatRules
      },
      {
        path: 'transfer',
        name: 'admin-transfer',
        component: TransferConfig
      },
      {
        path: 'knowledge',
        name: 'admin-knowledge',
        component: KnowledgeBase
      },
      {
        path: 'script',
        name: 'admin-script',
        component: ScriptConfig
      },
      {
        path: 'account',
        name: 'admin-account',
        component: AccountManage
      },
      {
        path: '',
        redirect: '/admin/model'
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫，检查登录状态
router.beforeEach((to, from, next) => {
  const user = localStorage.getItem('user')
  
  console.log('路由守卫:', to.path, 'from:', from.path, '用户:', user ? '已登录' : '未登录')
  
  if (to.path !== '/' && !user) {
    // 未登录，重定向到登录页
    console.log('未登录，重定向到登录页')
    next('/')
  } else if (to.path === '/' && user) {
    // 已登录，重定向到聊天页
    console.log('已登录，重定向到聊天页')
    next('/chat')
  } else {
    console.log('正常导航到:', to.path)
    next()
  }
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
})

export default router
