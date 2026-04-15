<template>
  <div class="rental-detail" v-loading="loading">
    <div class="container" v-if="rental">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/rental' }">租房</el-breadcrumb-item>
        <el-breadcrumb-item>{{ rental.title }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-row :gutter="40" class="detail-content">
        <!-- 左侧图片 -->
        <el-col :xs="24" :sm="24" :md="14">
          <div class="image-section">
            <el-carousel height="450px" class="main-carousel">
              <el-carousel-item v-for="(img, index) in rental.images" :key="index">
                <img :src="img || 'https://via.placeholder.com/600x450'" class="carousel-image" />
              </el-carousel-item>
              <el-carousel-item v-if="!rental.images || rental.images.length === 0">
                <img src="https://via.placeholder.com/600x450" class="carousel-image" />
              </el-carousel-item>
            </el-carousel>

            <div class="image-thumbnails" v-if="rental.images && rental.images.length > 1">
              <div
                v-for="(img, index) in rental.images"
                :key="index"
                class="thumbnail"
                :class="{ active: currentImageIndex === index }"
                @click="currentImageIndex = index"
              >
                <img :src="img" />
              </div>
            </div>
          </div>

          <!-- 房源描述 -->
          <div class="description-section">
            <h2>房源描述</h2>
            <div class="description-content">
              <p>{{ rental.description || '暂无详细描述' }}</p>
            </div>
          </div>

          <!-- 设施配置 -->
          <div class="facilities-section" v-if="rental.facilities && rental.facilities.length">
            <h2>设施配置</h2>
            <div class="facilities-grid">
              <div v-for="facility in rental.facilities" :key="facility" class="facility-item">
                <span class="facility-icon">{{ getFacilityIcon(facility) }}</span>
                <span class="facility-name">{{ facility }}</span>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右侧信息 -->
        <el-col :xs="24" :sm="24" :md="10">
          <div class="info-section">
            <h1 class="rental-title">{{ rental.title }}</h1>

            <div class="price-section">
              <span class="price">¥{{ rental.price }}</span>
              <span class="unit">元/月</span>
            </div>

            <div class="basic-info">
              <div class="info-item">
                <span class="label">租赁方式</span>
                <span class="value">{{ getTypeName(rental.type) }}</span>
              </div>
              <div class="info-item">
                <span class="label">面积</span>
                <span class="value">{{ rental.area }}㎡</span>
              </div>
              <div class="info-item">
                <span class="label">小区</span>
                <span class="value">{{ rental.location?.community || '暂无' }}</span>
              </div>
              <div class="info-item">
                <span class="label">地址</span>
                <span class="value">{{ rental.location?.address || '暂无' }}</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons">
              <el-button type="primary" size="large" @click="handleFavorite">
                <el-icon><Star /></el-icon>
                {{ isFavorited ? '已收藏' : '收藏' }}
              </el-button>
              <el-button type="success" size="large" @click="showAppointmentDialog = true">
                <el-icon><Calendar /></el-icon>
                预约看房
              </el-button>
            </div>

            <!-- 联系方式 -->
            <div class="contact-section">
              <h3>联系方式</h3>
              <div class="contact-item">
                <el-icon><Phone /></el-icon>
                <span>{{ rental.contact || '暂无' }}</span>
              </div>
              <div class="contact-tip">
                <el-icon><InfoFilled /></el-icon>
                <span>联系时请说明是在邻里通看到的</span>
              </div>
            </div>
          </div>

          <!-- 发布者信息 -->
          <div class="publisher-section">
            <h3>发布者信息</h3>
            <div class="publisher-info">
              <el-avatar :size="60" src="https://via.placeholder.com/60" />
              <div class="publisher-detail">
                <span class="publisher-name">{{ publisherName }}</span>
                <span class="publisher-time">发布于 {{ formatTime(rental.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-col>
      </el-row>

      <!-- 推荐房源 -->
      <div class="recommendations" v-if="recommendations.length">
        <h2>推荐房源</h2>
        <el-row :gutter="20">
          <el-col :xs="12" :sm="8" :md="6" v-for="item in recommendations" :key="item.id">
            <el-card shadow="hover" class="recommend-card" @click="goToDetail(item.id)">
              <img :src="item.images?.[0] || 'https://via.placeholder.com/200x150'" class="recommend-image" />
              <div class="recommend-info">
                <p class="recommend-title">{{ item.title }}</p>
                <p class="recommend-price">¥{{ item.price }}/月</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 预约看房对话框 -->
    <el-dialog v-model="showAppointmentDialog" title="预约看房" width="500px">
      <el-form ref="appointmentFormRef" :model="appointmentForm" :rules="appointmentRules">
        <el-form-item label="您的姓名" prop="name">
          <el-input v-model="appointmentForm.name" placeholder="请输入您的姓名" />
        </el-form-item>
        <el-form-item label="联系电话" prop="phone">
          <el-input v-model="appointmentForm.phone" placeholder="请输入联系电话" />
        </el-form-item>
        <el-form-item label="期望看房时间" prop="visit_time">
          <el-date-picker
            v-model="appointmentForm.visit_time"
            type="datetime"
            placeholder="选择日期和时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="备注">
          <el-input
            v-model="appointmentForm.message"
            type="textarea"
            :rows="3"
            placeholder="如有其他要求请备注"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAppointmentDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAppointment">确认预约</el-button>
      </template>
    </el-dialog>

    <!-- 加载失败 -->
    <el-empty v-if="!loading && !rental" description="房源不存在或已被删除" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { rentalApi } from '../../api/rental'
import { ElMessage } from 'element-plus'
import { Star, Calendar, Phone, InfoFilled } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const rental = ref(null)
const isFavorited = ref(false)
const currentImageIndex = ref(0)
const recommendations = ref([])
const showAppointmentDialog = ref(false)
const appointmentFormRef = ref(null)

const appointmentForm = reactive({
  name: '',
  phone: '',
  visit_time: '',
  message: ''
})

const appointmentRules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  phone: [
    { required: true, message: '请输入电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ],
  visit_time: [{ required: true, message: '请选择看房时间', trigger: 'change' }]
}

const publisherName = computed(() => {
  return rental.value?.publisher_id ? '用户' + rental.value.publisher_id.slice(-4) : '匿名用户'
})

const getTypeName = (type) => {
  const types = { whole: '整租', shared: '合租', single: '单间' }
  return types[type] || type
}

const getFacilityIcon = (facility) => {
  const icons = {
    '空调': '❄️', '冰箱': '🧊', '洗衣机': '👕', '热水器': '🚿',
    '床': '🛏️', '沙发': '🛋️', '电视': '📺', '网络': '📶',
    '暖气': '🔥', '衣柜': '🗄️', '厨房': '🍳', '卫生间': '🚽'
  }
  return icons[facility] || '✓'
}

const formatTime = (time) => {
  if (!time) return '未知'
  const date = new Date(time)
  const now = new Date()
  const diff = now - date
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (days === 0) return '今天'
  if (days === 1) return '昨天'
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString('zh-CN')
}

const fetchRentalDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    rental.value = await rentalApi.getDetail(id)
  } catch (error) {
    console.error('获取房源详情失败', error)
    ElMessage.error('获取房源详情失败')
  } finally {
    loading.value = false
  }
}

const fetchRecommendations = async () => {
  try {
    const response = await rentalApi.getList({ page: 1, page_size: 4 })
    recommendations.value = (response.data || []).filter(item => item.id !== rental.value?.id)
  } catch (error) {
    console.error('获取推荐失败', error)
  }
}

const handleFavorite = async () => {
  try {
    await rentalApi.favorite(rental.value.id)
    isFavorited.value = !isFavorited.value
    ElMessage.success(isFavorited.value ? '收藏成功' : '取消收藏')
  } catch (error) {
    ElMessage.error('操作失败，请先登录')
    router.push('/user/login')
  }
}

const handleAppointment = async () => {
  if (!appointmentFormRef.value) return

  await appointmentFormRef.value.validate(async (valid) => {
    if (!valid) return

    try {
      // TODO: 调用预约接口
      ElMessage.success('预约成功！我们会尽快与您联系')
      showAppointmentDialog.value = false
    } catch (error) {
      ElMessage.error('预约失败，请稍后重试')
    }
  })
}

const goToDetail = (id) => {
  router.push(`/rental/${id}`)
  window.scrollTo(0, 0)
}

onMounted(() => {
  fetchRentalDetail()
  fetchRecommendations()
})
</script>

<style scoped>
.rental-detail {
  min-height: 100vh;
  background-color: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.detail-content {
  margin-top: 30px;
}

.image-section {
  background: white;
  border-radius: 8px;
  padding: 15px;
}

.main-carousel {
  border-radius: 8px;
  overflow: hidden;
}

.carousel-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-thumbnails {
  display: flex;
  gap: 10px;
  margin-top: 15px;
  overflow-x: auto;
}

.thumbnail {
  width: 80px;
  height: 60px;
  border-radius: 4px;
  overflow: hidden;
  cursor: pointer;
  border: 2px solid transparent;
  flex-shrink: 0;
}

.thumbnail.active {
  border-color: #409eff;
}

.thumbnail img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.description-section,
.facilities-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.description-section h2,
.facilities-section h2 {
  font-size: 20px;
  margin-bottom: 15px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.description-content {
  color: #666;
  line-height: 1.8;
  white-space: pre-wrap;
}

.facilities-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
  gap: 15px;
}

.facility-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 8px;
}

.facility-icon {
  font-size: 24px;
  margin-bottom: 5px;
}

.facility-name {
  font-size: 12px;
  color: #666;
}

.info-section {
  background: white;
  border-radius: 8px;
  padding: 25px;
}

.rental-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
}

.price-section {
  background: #fff5f5;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.price {
  font-size: 36px;
  color: #f56c6c;
  font-weight: bold;
}

.unit {
  font-size: 16px;
  color: #999;
  margin-left: 5px;
}

.basic-info {
  margin-bottom: 25px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid #f0f0f0;
}

.info-item:last-child {
  border-bottom: none;
}

.info-item .label {
  color: #999;
}

.info-item .value {
  color: #333;
  font-weight: 500;
}

.action-buttons {
  display: flex;
  gap: 15px;
  margin-bottom: 25px;
}

.action-buttons .el-button {
  flex: 1;
  height: 50px;
  font-size: 16px;
}

.contact-section {
  background: #f9f9f9;
  padding: 20px;
  border-radius: 8px;
}

.contact-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  color: #333;
  margin-bottom: 10px;
}

.contact-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #999;
  font-size: 12px;
}

.publisher-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.publisher-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
}

.publisher-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.publisher-detail {
  display: flex;
  flex-direction: column;
}

.publisher-name {
  font-size: 16px;
  font-weight: 500;
}

.publisher-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.recommendations {
  margin-top: 40px;
  padding-bottom: 40px;
}

.recommendations h2 {
  font-size: 22px;
  margin-bottom: 20px;
}

.recommend-card {
  cursor: pointer;
  margin-bottom: 15px;
}

.recommend-image {
  width: 100%;
  height: 120px;
  object-fit: cover;
}

.recommend-info {
  padding: 10px 0;
}

.recommend-title {
  font-size: 14px;
  color: #333;
  margin-bottom: 5px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.recommend-price {
  color: #f56c6c;
  font-weight: bold;
}
</style>
