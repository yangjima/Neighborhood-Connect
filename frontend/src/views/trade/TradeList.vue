<template>
  <div class="trade-list">
    <div class="search-bar">
      <el-input
        v-model="searchQuery"
        placeholder="搜索二手商品..."
        class="search-input"
        @keyup.enter="handleSearch"
      >
        <template #append>
          <el-button @click="handleSearch">搜索</el-button>
        </template>
      </el-input>

      <el-button type="primary" @click="goToPublish">发布闲置</el-button>
    </div>

    <div class="filters">
      <el-select v-model="filters.category" placeholder="商品分类" @change="handleFilter">
        <el-option label="全部" value="" />
        <el-option label="家具" value="furniture" />
        <el-option label="家电" value="appliance" />
        <el-option label="其他" value="other" />
      </el-select>

      <el-select v-model="filters.condition" placeholder="新旧程度" @change="handleFilter">
        <el-option label="全部" value="" />
        <el-option label="全新" value="new" />
        <el-option label="九成新" value="like_new" />
        <el-option label="八成新" value="good" />
        <el-option label="七成新及以下" value="fair" />
      </el-select>

      <el-select v-model="filters.priceRange" placeholder="价格区间" @change="handleFilter">
        <el-option label="全部" value="" />
        <el-option label="100以下" value="0-100" />
        <el-option label="100-500" value="100-500" />
        <el-option label="500-1000" value="500-1000" />
        <el-option label="1000以上" value="1000-999999" />
      </el-select>
    </div>

    <el-row :gutter="20" v-loading="loading">
      <el-col :xs="12" :sm="12" :md="8" :lg="6" v-for="item in items" :key="item.id">
        <el-card shadow="hover" class="item-card" @click="goToDetail(item.id)">
          <div class="image-wrapper">
            <img :src="item.images?.[0] || 'https://picsum.photos/seed/img/200/200'" class="item-image" />
            <el-tag
              v-if="item.condition"
              :type="getConditionType(item.condition)"
              class="condition-tag"
              size="small"
            >
              {{ getConditionName(item.condition) }}
            </el-tag>
          </div>
          <div class="item-info">
            <h3 class="item-title">{{ item.title }}</h3>
            <div class="item-meta">
              <span class="price">¥{{ item.price }}</span>
              <span class="category">{{ getCategoryName(item.category) }}</span>
            </div>
            <p class="location" v-if="item.location">{{ item.location }}</p>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-empty v-if="!loading && items.length === 0" description="暂无商品" />

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
import { tradeApi } from '../../api/trade'
import { ElMessage } from 'element-plus'

const router = useRouter()

const searchQuery = ref('')
const filters = ref({
  category: '',
  condition: '',
  priceRange: ''
})

const items = ref([])
const loading = ref(false)
const currentPage = ref(1)
const pageSize = ref(12)
const total = ref(0)

const getCategoryName = (category) => {
  const categories = { furniture: '家具', appliance: '家电', other: '其他' }
  return categories[category] || category
}

const getConditionName = (condition) => {
  const conditions = { new: '全新', like_new: '九成新', good: '八成新', fair: '七成新及以下' }
  return conditions[condition] || condition
}

const getConditionType = (condition) => {
  const types = { new: 'success', like_new: 'primary', good: 'warning', fair: 'info' }
  return types[condition] || 'info'
}

const fetchItems = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      page_size: pageSize.value
    }

    if (filters.value.category) params.category = filters.value.category
    if (filters.value.condition) params.condition = filters.value.condition

    if (filters.value.priceRange) {
      const [min, max] = filters.value.priceRange.split('-')
      params.min_price = parseFloat(min)
      params.max_price = parseFloat(max)
    }

    const response = await tradeApi.getList(params)
    items.value = response.data || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('获取商品列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    fetchItems()
    return
  }

  loading.value = true
  try {
    const response = await tradeApi.search({ q: searchQuery.value })
    items.value = response.data || []
    total.value = response.total || 0
  } catch (error) {
    ElMessage.error('搜索失败')
  } finally {
    loading.value = false
  }
}

const handleFilter = () => {
  currentPage.value = 1
  fetchItems()
}

const handlePageChange = (page) => {
  currentPage.value = page
  fetchItems()
  window.scrollTo(0, 0)
}

const goToDetail = (id) => {
  router.push(`/trade/${id}`)
}

const goToPublish = () => {
  router.push('/trade/publish')
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.trade-list {
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

.filters .el-select {
  width: 150px;
}

.item-card {
  cursor: pointer;
  margin-bottom: 20px;
  transition: transform 0.3s;
}

.item-card:hover {
  transform: translateY(-5px);
}

.image-wrapper {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.item-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.condition-tag {
  position: absolute;
  top: 10px;
  right: 10px;
}

.item-info {
  padding: 12px 0;
}

.item-title {
  font-size: 16px;
  color: #333;
  margin: 0 0 10px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.item-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.price {
  font-size: 20px;
  color: #f56c6c;
  font-weight: bold;
}

.category {
  font-size: 12px;
  color: #999;
}

.location {
  font-size: 12px;
  color: #999;
  margin: 0;
}

.pagination {
  margin-top: 30px;
  display: flex;
  justify-content: center;
}
</style>
