<template>
  <el-container class="layout-container">
    <!-- 顶部导航 -->
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="router.push('/')">
          <span class="logo-icon">🏘️</span>
          <span class="logo-text">邻里通</span>
        </div>

        <el-menu
          mode="horizontal"
          :default-active="activeMenu"
          class="nav-menu"
          :ellipsis="false"
        >
          <el-menu-item index="/" @click="router.push('/')">首页</el-menu-item>
          <el-menu-item index="/rental" @click="router.push('/rental')">租房</el-menu-item>
          <el-menu-item index="/trade" @click="router.push('/trade')">二手交易</el-menu-item>
        </el-menu>

        <div class="header-actions">
          <el-button type="primary" @click="router.push('/trade/publish')">
            <el-icon><Plus /></el-icon>
            发布闲置
          </el-button>

          <template v-if="userStore.token">
            <el-dropdown @command="handleUserCommand">
              <div class="user-info">
                <el-avatar :size="36" :icon="UserFilled" />
                <span class="username">{{ userStore.userInfo?.nickname || '用户' }}</span>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="profile">个人中心</el-dropdown-item>
                  <el-dropdown-item command="my-rentals">我的房源</el-dropdown-item>
                  <el-dropdown-item command="my-items">我的闲置</el-dropdown-item>
                  <el-dropdown-item command="orders">我的订单</el-dropdown-item>
                  <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>

          <template v-else>
            <el-button @click="router.push('/user/login')">登录</el-button>
          </template>
        </div>
      </div>
    </el-header>

    <!-- 主内容区 -->
    <el-main class="main-content">
      <router-view />
    </el-main>

    <!-- 底部 -->
    <el-footer class="footer">
      <div class="footer-content">
        <div class="footer-links">
          <a href="#">关于我们</a>
          <a href="#">联系我们</a>
          <a href="#">用户协议</a>
          <a href="#">隐私政策</a>
        </div>
        <p class="copyright">© 2024 邻里通 - 连接社区，服务生活</p>
      </div>
    </el-footer>
  </el-container>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UserFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const activeMenu = computed(() => {
  if (route.path.startsWith('/rental')) return '/rental'
  if (route.path.startsWith('/trade')) return '/trade'
  return '/'
})

const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      router.push('/user/profile')
      break
    case 'my-rentals':
      router.push('/user/my-rentals')
      break
    case 'my-items':
      router.push('/user/my-items')
      break
    case 'orders':
      router.push('/user/orders')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        userStore.logout()
        ElMessage.success('已退出登录')
        router.push('/')
      } catch {
        // 取消操作
      }
      break
  }
}
</script>

<style scoped>
.layout-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: white;
  border-bottom: 1px solid #e4e7ed;
  padding: 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  padding: 0 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  margin-right: 40px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 22px;
  font-weight: bold;
  color: #409eff;
}

.nav-menu {
  flex: 1;
  border-bottom: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 5px 10px;
  border-radius: 20px;
  transition: background-color 0.3s;
}

.user-info:hover {
  background-color: #f5f7fa;
}

.username {
  font-size: 14px;
  color: #333;
}

.main-content {
  flex: 1;
  padding: 0;
  background-color: #f5f5f5;
}

.footer {
  background: #2c3e50;
  color: white;
  padding: 40px 20px;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.footer-links {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-bottom: 20px;
}

.footer-links a {
  color: #bdc3c7;
  text-decoration: none;
  transition: color 0.3s;
}

.footer-links a:hover {
  color: white;
}

.copyright {
  color: #7f8c8d;
  font-size: 14px;
}

:deep(.el-menu-item) {
  font-size: 16px;
}
</style>
