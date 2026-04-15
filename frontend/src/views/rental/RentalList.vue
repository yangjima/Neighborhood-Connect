<template>
  <div class="rental-list">
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索房源..."
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>

      <el-button type="primary" @click="goToPublish">发布房源</el-button>
    </div>

    <div class="filters">
      <el-select v-model="filters.type" placeholder="租赁类型" @change="handleFilter">
        <el-option label="全部" value="" />
        <el-option label="整租" value="whole" />
        <el-option label="合租" value="shared" />
        <el-option label="单间" value="single" />
      </el-select>

      <el-select v-model="filters.priceRange" placeholder="价格范围" @change="handleFilter">
        <el-option label="全部" value="" />
        <el-option label="1000以下" value="0-1000" />
        <el-option label="1000-2000" value="1000-2000" />
        <el-option label="2000-3000" value="2000-3000" />
        <el-option label="3000以上" value="3000-999999" />
      </el-select>

      <el-input v-model="filters.location" placeholder="位置" @change="handleFilter" />
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :xs="24" :sm="12" :md="8" v-for="rental in rentals" :key="rental.id">
        <el-card shadow="hover" class="rental-card" @click="goToDetail(rental.id)">
          <img :src="rental.images[0] || 'https://picsum.photos/seed/img/400/300'" class="rental-image" />
          <div class="rental-info">
            <h3>{{ rental.title }}</h3>
            <p class="price">¥{{ rental.price }}/月</p>
            <p class="details">{{ rental.type }} | {{ rental.area }}㎡</p>
            <p class="location">{{ rental.location.community }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-pagination
      v-if="total > 0"
      class="pagination"
      :current-page="currentPage"
      :page-size="pageSize"
      :total="total"
      layout="prev, pager, next"
      @current-change="handlePageChange"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { rentalApi } from '../../api/rental'
import { ElMessage } from 'element-plus'

const router = useRouter()

const searchQuery = ref('')
const filters = ref({
  type: '',
  priceRange: '',
  location: ''
})

const rentals = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const fetchRentals = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value,
      ...filters.value
    }
    const response = await rentalApi.getList(params)
    rentals.value = response.data
    total.value = response.total
  } catch (error) {
    ElMessage.error('获取房源列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    fetchRentals()
    return
  }

  loading.value = true
  try {
    const response = await rentalApi.search({ q: searchQuery.value })
    rentals.value = response.data
    total.value = response.total
  } catch (error) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  fetchRentals()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchRentals()
}

const goToDetail = (id) => {
  router.push(`/rental/${id}`)
}

const goToPublish = () => {
  router.push('/rental/publish')
}

onMounted(() => {
  fetchRentals()
})
</script>

<style scoped>
.rental-list {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
}

.filters {
  display: flex;
  gap: 10px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filters .el-select,
.filters .el-input {
  width: 200px;
}

.rental-card {
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.rental-card:hover {
  transform: translateY(-5px);
}

.rental-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.rental-info {
  padding: 15px 0;
}

.rental-info h3 {
  margin: 0 0 10px 0;
  font-size: 18px;
  color: #333;
}

.price {
  color: #f56c6c;
  font-size: 24px;
  font-weight: bold;
  margin: 5px 0;
}

.details {
  color: #666;
  font-size: 14px;
  margin: 5px 0;
}

.location {
  color: #909399;
  font-size: 14px;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}
</style>
