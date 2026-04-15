<template>
  <div class="profile-page">
    <div class="container">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="6">
          <el-card class="user-card">
            <div class="user-info">
              <el-avatar :size="80" :src="userInfo?.avatar" />
              <h3>{{ userInfo?.nickname || '用户' }}</h3>
              <p class="user-type">{{ getUserTypeName(userInfo?.userType) }}</p>
            </div>
            <el-menu :default-active="activeMenu" @select="handleMenuSelect">
              <el-menu-item index="info">
                <el-icon><User /></el-icon>
                <span>个人信息</span>
              </el-menu-item>
              <el-menu-item index="items">
                <el-icon><Goods /></el-icon>
                <span>我的发布</span>
              </el-menu-item>
              <el-menu-item index="orders">
                <el-icon><Document /></el-icon>
                <span>我的订单</span>
              </el-menu-item>
              <el-menu-item index="favorites">
                <el-icon><Star /></el-icon>
                <span>我的收藏</span>
              </el-menu-item>
            </el-menu>
          </el-card>
        </el-col>

        <el-col :xs="24" :sm="18">
          <el-card class="content-card">
            <template #header>
              <div class="card-header">
                <span>个人信息</span>
                <el-button type="primary" size="small" @click="showEditDialog = true">
                  编辑资料
                </el-button>
              </div>
            </template>

            <div class="info-grid">
              <div class="info-item">
                <span class="label">手机号</span>
                <span class="value">{{ userInfo?.phone || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">昵称</span>
                <span class="value">{{ userInfo?.nickname || '未设置' }}</span>
              </div>
              <div class="info-item">
                <span class="label">用户类型</span>
                <span class="value">{{ getUserTypeName(userInfo?.userType) }}</span>
              </div>
              <div class="info-item">
                <span class="label">注册时间</span>
                <span class="value">{{ formatTime(userInfo?.createdAt) }}</span>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <el-dialog v-model="showEditDialog" title="编辑资料" width="500px">
      <el-form :model="editForm" label-width="80px">
        <el-form-item label="昵称">
          <el-input v-model="editForm.nickname" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="头像">
          <el-upload
            action="#"
            :show-file-list="false"
            :before-upload="handleAvatarUpload"
          >
            <el-avatar :size="60" :src="editForm.avatar" />
            <span class="upload-tip">点击上传</span>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showEditDialog = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../../store/user'
import { authApi } from '../../api/auth'
import { ElMessage } from 'element-plus'
import { User, Goods, Document, Star } from '@element-plus/icons-vue'

const router = useRouter()
const userStore = useUserStore()

const activeMenu = ref('info')
const showEditDialog = ref(false)

const userInfo = ref({
  phone: '138****8888',
  nickname: '邻里用户',
  userType: 'resident',
  avatar: null,
  createdAt: '2024-01-01'
})

const editForm = reactive({
  nickname: '',
  avatar: ''
})

const getUserTypeName = (type) => {
  const types = { resident: '居民', merchant: '商家', property: '物业' }
  return types[type] || '未知'
}

const formatTime = (time) => {
  if (!time) return '未知'
  return new Date(time).toLocaleDateString('zh-CN')
}

const handleMenuSelect = (index) => {
  switch (index) {
    case 'info':
      break
    case 'items':
      router.push('/user/my-items')
      break
    case 'orders':
      router.push('/user/orders')
      break
    case 'favorites':
      ElMessage.info('收藏功能开发中')
      break
  }
}

const handleAvatarUpload = (file) => {
  const url = URL.createObjectURL(file.raw)
  editForm.avatar = url
  return false
}

const handleSave = () => {
  userInfo.value.nickname = editForm.nickname
  userInfo.value.avatar = editForm.avatar
  showEditDialog.value = false
  ElMessage.success('保存成功')
}

onMounted(async () => {
  if (userStore.token) {
    try {
      const response = await authApi.getProfile()
      userInfo.value = response
    } catch (error) {
      console.error('获取用户信息失败', error)
    }
  }

  editForm.nickname = userInfo.value.nickname
  editForm.avatar = userInfo.value.avatar
})
</script>

<style scoped>
.profile-page {
  min-height: calc(100vh - 120px);
  background-color: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.user-card {
  text-align: center;
}

.user-info {
  padding: 20px 0;
}

.user-info h3 {
  margin: 15px 0 5px 0;
}

.user-type {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.content-card {
  min-height: 400px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 8px;
}

.info-item .label {
  color: #999;
  font-size: 14px;
  margin-bottom: 8px;
}

.info-item .value {
  color: #333;
  font-size: 16px;
  font-weight: 500;
}

.upload-tip {
  margin-left: 10px;
  color: #409eff;
  font-size: 12px;
}
</style>
