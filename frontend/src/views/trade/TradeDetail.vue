<template>
  <div class="trade-detail" v-loading="loading">
    <div class="container" v-if="item">
      <el-breadcrumb separator="/">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item :to="{ path: '/trade' }">二手交易</el-breadcrumb-item>
        <el-breadcrumb-item>{{ item.title }}</el-breadcrumb-item>
      </el-breadcrumb>

      <el-row :gutter="40" class="detail-content">
        <!-- 左侧图片 -->
        <el-col :xs="24" :sm="24" :md="14">
          <div class="image-section">
            <el-carousel height="450px" class="main-carousel">
              <el-carousel-item v-for="(img, index) in item.images" :key="index">
                <img :src="img || 'https://via.placeholder.com/600x450'" class="carousel-image" />
              </el-carousel-item>
              <el-carousel-item v-if="!item.images || item.images.length === 0">
                <img src="https://via.placeholder.com/600x450" class="carousel-image" />
              </el-carousel-item>
            </el-carousel>
          </div>

          <!-- 商品描述 -->
          <div class="description-section">
            <h2>商品描述</h2>
            <div class="description-content">
              <p>{{ item.description || '暂无详细描述' }}</p>
            </div>
          </div>

          <!-- 商品参数 -->
          <div class="specs-section">
            <h2>商品参数</h2>
            <div class="specs-grid">
              <div class="spec-item">
                <span class="spec-label">分类</span>
                <span class="spec-value">{{ getCategoryName(item.category) }}</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">成色</span>
                <span class="spec-value">
                  <el-tag :type="getConditionType(item.condition)">
                    {{ getConditionName(item.condition) }}
                  </el-tag>
                </span>
              </div>
              <div class="spec-item">
                <span class="spec-label">交易方式</span>
                <span class="spec-value">当面交易 / 在线支付</span>
              </div>
              <div class="spec-item">
                <span class="spec-label">发布时间</span>
                <span class="spec-value">{{ formatTime(item.created_at) }}</span>
              </div>
            </div>
          </div>
        </el-col>

        <!-- 右侧信息 -->
        <el-col :xs="24" :sm="24" :md="10">
          <div class="info-section">
            <div class="status-tag" v-if="item.status !== 'available'">
              <el-tag type="info" size="large">{{ getStatusName(item.status) }}</el-tag>
            </div>

            <h1 class="item-title">{{ item.title }}</h1>

            <div class="price-section">
              <span class="price">¥{{ item.price }}</span>
              <span class="original-price">原价 ¥{{ Math.round(item.price * 1.5) }}</span>
            </div>

            <div class="basic-info">
              <div class="info-item">
                <span class="label">商品分类</span>
                <span class="value">{{ getCategoryName(item.category) }}</span>
              </div>
              <div class="info-item">
                <span class="label">新旧程度</span>
                <span class="value">
                  <el-tag :type="getConditionType(item.condition)" size="small">
                    {{ getConditionName(item.condition) }}
                  </el-tag>
                </span>
              </div>
              <div class="info-item">
                <span class="label">所在地区</span>
                <span class="value">{{ item.location || '暂无' }}</span>
              </div>
            </div>

            <!-- 操作按钮 -->
            <div class="action-buttons" v-if="item.status === 'available'">
              <el-button type="primary" size="large" @click="handleBuy">
                <el-icon><ShoppingCart /></el-icon>
                立即购买
              </el-button>
              <el-button size="large" @click="handleContact">
                <el-icon><ChatDotRound /></el-icon>
                联系卖家
              </el-button>
            </div>

            <div class="action-buttons" v-else>
              <el-button type="info" size="large" disabled>
                {{ getStatusName(item.status) }}
              </el-button>
            </div>
          </div>

          <!-- 卖家信息 -->
          <div class="seller-section">
            <h3>卖家信息</h3>
            <div class="seller-info">
              <el-avatar :size="60" :icon="UserFilled" />
              <div class="seller-detail">
                <span class="seller-name">{{ sellerName }}</span>
                <div class="seller-stats">
                  <span>在售商品 {{ sellerStats.onSale }}</span>
                  <span>已完成交易 {{ sellerStats.completed }}</span>
                </div>
              </div>
            </div>
            <el-button class="follow-button" plain>
              <el-icon><Plus /></el-icon>
              关注卖家
            </el-button>
          </div>

          <!-- 安全提示 -->
          <div class="safety-tips">
            <h4>交易安全提示</h4>
            <ul>
              <li>建议使用平台担保交易</li>
              <li>当面交易时注意人身安全</li>
              <li>不要轻信低价诱惑</li>
              <li>保留聊天记录作为证据</li>
            </ul>
          </div>
        </el-col>
      </el-row>

      <!-- 推荐商品 -->
      <div class="recommendations" v-if="recommendations.length">
        <h2>相似商品</h2>
        <el-row :gutter="20">
          <el-col :xs="12" :sm="8" :md="6" v-for="rec in recommendations" :key="rec.id">
            <el-card shadow="hover" class="recommend-card" @click="goToDetail(rec.id)">
              <img :src="rec.images?.[0] || 'https://via.placeholder.com/200x150'" class="recommend-image" />
              <div class="recommend-info">
                <p class="recommend-title">{{ rec.title }}</p>
                <p class="recommend-price">¥{{ rec.price }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>

    <!-- 购买对话框 -->
    <el-dialog v-model="showBuyDialog" title="确认购买" width="500px">
      <div class="buy-dialog-content">
        <div class="item-summary">
          <img :src="item?.images?.[0]" class="item-thumb" />
          <div class="item-info">
            <p class="item-title">{{ item?.title }}</p>
            <p class="item-price">¥{{ item?.price }}</p>
          </div>
        </div>

        <el-divider />

        <div class="payment-methods">
          <h4>选择支付方式</h4>
          <el-radio-group v-model="paymentMethod">
            <el-radio label="wechat">
              <span class="payment-icon">💳</span> 微信支付
            </el-radio>
            <el-radio label="alipay">
              <span class="payment-icon">💰</span> 支付宝
            </el-radio>
          </el-radio-group>
        </div>
      </div>

      <template #footer>
        <el-button @click="showBuyDialog = false">取消</el-button>
        <el-button type="primary" @click="confirmPurchase">确认支付 ¥{{ item?.price }}</el-button>
      </template>
    </el-dialog>

    <!-- 联系卖家对话框 -->
    <el-dialog v-model="showContactDialog" title="联系卖家" width="500px">
      <div class="contact-content">
        <p>您可以拨打卖家电话或发送站内消息联系卖家</p>
        <div class="contact-actions">
          <el-button type="primary" @click="handleCall">
            <el-icon><Phone /></el-icon>
            拨打电话
          </el-button>
          <el-button @click="handleSendMessage">
            <el-icon><ChatDotRound /></el-icon>
            发送消息
          </el-button>
        </div>
      </div>
    </el-dialog>

    <el-empty v-if="!loading && !item" description="商品不存在或已下架" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { tradeApi } from '../../api/trade'
import { ElMessage } from 'element-plus'
import { ShoppingCart, ChatDotRound, UserFilled, Plus, Phone } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const item = ref(null)
const recommendations = ref([])
const showBuyDialog = ref(false)
const showContactDialog = ref(false)
const paymentMethod = ref('wechat')

const sellerName = computed(() => {
  return item.value?.seller_id ? '用户' + item.value.seller_id.slice(-4) : '匿名用户'
})

const sellerStats = ref({
  onSale: 0,
  completed: 0
})

const getCategoryName = (category) => {
  const categories = {
    furniture: '家具',
    appliance: '家电',
    other: '其他'
  }
  return categories[category] || category
}

const getConditionName = (condition) => {
  const conditions = {
    new: '全新',
    like_new: '九成新',
    good: '八成新',
    fair: '七成新及以下'
  }
  return conditions[condition] || condition
}

const getConditionType = (condition) => {
  const types = {
    new: 'success',
    like_new: 'primary',
    good: 'warning',
    fair: 'info'
  }
  return types[condition] || 'info'
}

const getStatusName = (status) => {
  const statuses = {
    available: '可售',
    reserved: '已预留',
    sold: '已售出'
  }
  return statuses[status] || status
}

const formatTime = (time) => {
  if (!time) return '未知'
  const date = new Date(time)
  return date.toLocaleDateString('zh-CN')
}

const fetchItemDetail = async () => {
  loading.value = true
  try {
    const id = route.params.id
    item.value = await tradeApi.getDetail(id)
  } catch (error) {
    console.error('获取商品详情失败', error)
    ElMessage.error('获取商品详情失败')
  } finally {
    loading.value = false
  }
}

const fetchRecommendations = async () => {
  try {
    const response = await tradeApi.getList({ page: 1, page_size: 4 })
    recommendations.value = (response.data || []).filter(i => i.id !== item.value?.id)
  } catch (error) {
    console.error('获取推荐失败', error)
  }
}

const handleBuy = () => {
  showBuyDialog.value = true
}

const confirmPurchase = async () => {
  try {
    await tradeApi.createOrder(item.value.id)
    ElMessage.success('订单创建成功，请支付')
    showBuyDialog.value = false
    router.push('/user/profile')
  } catch (error) {
    ElMessage.error('创建订单失败')
  }
}

const handleContact = () => {
  showContactDialog.value = true
}

const handleCall = () => {
  ElMessage.info('请联系平台获取卖家联系方式')
}

const handleSendMessage = () => {
  ElMessage.info('消息功能开发中')
}

const goToDetail = (id) => {
  router.push(`/trade/${id}`)
  window.scrollTo(0, 0)
}

onMounted(() => {
  fetchItemDetail()
  fetchRecommendations()
})
</script>

<style scoped>
.trade-detail {
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

.description-section,
.specs-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.description-section h2,
.specs-section h2 {
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

.specs-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.spec-item {
  display: flex;
  justify-content: space-between;
  padding: 10px;
  background: #f9f9f9;
  border-radius: 6px;
}

.spec-label {
  color: #999;
}

.spec-value {
  color: #333;
  font-weight: 500;
}

.info-section {
  background: white;
  border-radius: 8px;
  padding: 25px;
  position: relative;
}

.status-tag {
  position: absolute;
  top: 25px;
  right: 25px;
}

.item-title {
  font-size: 24px;
  color: #333;
  margin-bottom: 20px;
  margin-top: 30px;
}

.price-section {
  background: linear-gradient(135deg, #fff5f5, #fff);
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  border: 1px solid #fde2e2;
}

.price {
  font-size: 36px;
  color: #f56c6c;
  font-weight: bold;
}

.original-price {
  font-size: 14px;
  color: #999;
  text-decoration: line-through;
  margin-left: 15px;
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
}

.action-buttons {
  display: flex;
  gap: 15px;
}

.action-buttons .el-button {
  flex: 1;
  height: 50px;
  font-size: 16px;
}

.seller-section {
  background: white;
  border-radius: 8px;
  padding: 20px;
  margin-top: 20px;
}

.seller-section h3 {
  font-size: 16px;
  margin-bottom: 15px;
}

.seller-info {
  display: flex;
  align-items: center;
  gap: 15px;
  margin-bottom: 15px;
}

.seller-detail {
  display: flex;
  flex-direction: column;
}

.seller-name {
  font-size: 16px;
  font-weight: 500;
}

.seller-stats {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.follow-button {
  width: 100%;
}

.safety-tips {
  background: #fffbe6;
  border: 1px solid #ffe58f;
  border-radius: 8px;
  padding: 15px;
  margin-top: 20px;
}

.safety-tips h4 {
  font-size: 14px;
  margin-bottom: 10px;
  color: #ad6800;
}

.safety-tips ul {
  margin: 0;
  padding-left: 20px;
  font-size: 12px;
  color: #8c6a0a;
}

.safety-tips li {
  margin-bottom: 5px;
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

.buy-dialog-content {
  padding: 10px 0;
}

.item-summary {
  display: flex;
  gap: 15px;
  align-items: center;
}

.item-thumb {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 8px;
}

.item-info {
  flex: 1;
}

.item-title {
  font-size: 16px;
  margin-bottom: 10px;
}

.item-price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
}

.payment-methods {
  margin-top: 20px;
}

.payment-methods h4 {
  margin-bottom: 15px;
}

.payment-icon {
  margin-right: 5px;
}

.contact-content {
  text-align: center;
}

.contact-content p {
  color: #666;
  margin-bottom: 20px;
}

.contact-actions {
  display: flex;
  gap: 15px;
  justify-content: center;
}
</style>
