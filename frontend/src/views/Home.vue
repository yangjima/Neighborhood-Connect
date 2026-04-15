<template>
  <div class="home">
    <el-carousel height="400px" class="banner">
      <el-carousel-item v-for="item in banners" :key="item.id">
        <div class="banner-item" :style="{ backgroundColor: item.color }">
          <h2>{{ item.title }}</h2>
          <p>{{ item.description }}</p>
        </div>
      </el-carousel-item>
    </el-carousel>

    <div class="container">
      <el-row :gutter="20" class="service-cards">
        <el-col :xs="24" :sm="12" :md="6" v-for="service in services" :key="service.id">
          <el-card shadow="hover" class="service-card" @click="navigateTo(service.path)">
            <div class="service-icon">{{ service.icon }}</div>
            <h3>{{ service.title }}</h3>
            <p>{{ service.description }}</p>
          </el-card>
        </el-col>
      </el-row>

      <div class="section">
        <h2>最新房源</h2>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" v-for="rental in latestRentals" :key="rental.id">
            <el-card shadow="hover" class="item-card" @click="goToDetail('rental', rental.id)">
              <img :src="rental.image" class="item-image" />
              <div class="item-info">
                <h4>{{ rental.title }}</h4>
                <p class="price">¥{{ rental.price }}/月</p>
                <p class="location">{{ rental.location }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <div class="section">
        <h2>二手好物</h2>
        <el-row :gutter="20">
          <el-col :xs="24" :sm="12" :md="8" v-for="item in latestTrades" :key="item.id">
            <el-card shadow="hover" class="item-card" @click="goToDetail('trade', item.id)">
              <img :src="item.image" class="item-image" />
              <div class="item-info">
                <h4>{{ item.title }}</h4>
                <p class="price">¥{{ item.price }}</p>
                <p class="condition">{{ item.condition }}</p>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const banners = ref([
  { id: 1, title: '邻里通', description: '连接社区，服务生活', color: '#409EFF' },
  { id: 2, title: '租房无忧', description: '海量房源，安心选择', color: '#67C23A' },
  { id: 3, title: '二手交易', description: '闲置变现，环保生活', color: '#E6A23C' }
])

const services = ref([
  { id: 1, icon: '🏠', title: '租房服务', description: '找房、租房一站式服务', path: '/rental' },
  { id: 2, icon: '🛋️', title: '二手交易', description: '家具家电闲置交易', path: '/trade' },
  { id: 3, icon: '🧹', title: '家政服务', description: '保洁维修预约', path: '/service' },
  { id: 4, icon: '💼', title: '兼职招聘', description: '本地兼职信息', path: '/job' }
])

const latestRentals = ref([])
const latestTrades = ref([])

const navigateTo = (path) => {
  router.push(path)
}

const goToDetail = (type, id) => {
  router.push(`/${type}/${id}`)
}

onMounted(() => {
  // TODO: 从API获取最新数据
  latestRentals.value = [
    { id: 1, title: '精装两室一厅', price: 3000, location: '朝阳区', image: 'https://picsum.photos/seed/house1/400/300' },
    { id: 2, title: '温馨单间出租', price: 1500, location: '海淀区', image: 'https://picsum.photos/seed/house2/400/300' },
    { id: 3, title: '合租主卧', price: 2000, location: '丰台区', image: 'https://picsum.photos/seed/house3/400/300' }
  ]

  latestTrades.value = [
    { id: 1, title: '九成新沙发', price: 800, condition: '九成新', image: 'https://picsum.photos/seed/sofa/400/300' },
    { id: 2, title: '宜家书桌', price: 300, condition: '八成新', image: 'https://picsum.photos/seed/desk/400/300' },
    { id: 3, title: '电视柜', price: 200, condition: '九成新', image: 'https://picsum.photos/seed/cabinet/400/300' }
  ]
})
</script>

<style scoped>
.home {
  min-height: 100vh;
  background-color: #f5f5f5;
}

.banner {
  margin-bottom: 40px;
}

.banner-item {
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  height: 100%;
  color: white;
}

.banner-item h2 {
  font-size: 48px;
  margin-bottom: 20px;
}

.banner-item p {
  font-size: 24px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.service-cards {
  margin-bottom: 60px;
}

.service-card {
  text-align: center;
  cursor: pointer;
  transition: transform 0.3s;
}

.service-card:hover {
  transform: translateY(-5px);
}

.service-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.service-card h3 {
  margin: 10px 0;
  font-size: 20px;
}

.service-card p {
  color: #666;
  font-size: 14px;
}

.section {
  margin-bottom: 60px;
}

.section h2 {
  margin-bottom: 20px;
  font-size: 28px;
  color: #333;
}

.item-card {
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.item-card:hover {
  transform: translateY(-5px);
}

.item-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.item-info {
  padding: 15px 0;
}

.item-info h4 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.price {
  color: #f56c6c;
  font-size: 20px;
  font-weight: bold;
  margin: 5px 0;
}

.location, .condition {
  color: #909399;
  font-size: 14px;
}
</style>
