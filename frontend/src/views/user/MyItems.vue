<template>
  <div class="my-items-page">
    <div class="container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>我的发布</span>
            <el-button type="primary" @click="$router.push('/trade/publish')">
              发布新商品
            </el-button>
          </div>
        </template>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="在售" name="available">
            <el-row :gutter="20" v-if="availableItems.length">
              <el-col :xs="12" :sm="8" :md="6" v-for="item in availableItems" :key="item.id">
                <el-card shadow="hover" class="item-card" @click="$router.push(`/trade/${item.id}`)">
                  <img :src="item.images?.[0]" class="item-image" />
                  <div class="item-info">
                    <h4>{{ item.title }}</h4>
                    <p class="price">¥{{ item.price }}</p>
                    <div class="actions">
                      <el-button size="small" @click.stop="handleEdit(item)">编辑</el-button>
                      <el-button size="small" type="danger" @click.stop="handleDelete(item)">删除</el-button>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            <el-empty v-else description="暂无在售商品" />
          </el-tab-pane>

          <el-tab-pane label="已售出" name="sold">
            <el-row :gutter="20" v-if="soldItems.length">
              <el-col :xs="12" :sm="8" :md="6" v-for="item in soldItems" :key="item.id">
                <el-card shadow="hover" class="item-card sold">
                  <img :src="item.images?.[0]" class="item-image" />
                  <div class="sold-overlay">已售出</div>
                  <div class="item-info">
                    <h4>{{ item.title }}</h4>
                    <p class="price">¥{{ item.price }}</p>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            <el-empty v-else description="暂无已售商品" />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { tradeApi } from '../../api/trade'
import { ElMessage, ElMessageBox } from 'element-plus'

const activeTab = ref('available')
const availableItems = ref([])
const soldItems = ref([])

const fetchMyItems = async () => {
  try {
    const response = await tradeApi.getList({ page: 1, page_size: 100 })
    // 模拟数据
    availableItems.value = [
      { id: '1', title: '九成新沙发', price: 800, images: ['https://via.placeholder.com/200'], status: 'available' },
      { id: '2', title: '宜家书桌', price: 300, images: ['https://via.placeholder.com/200'], status: 'available' }
    ]
    soldItems.value = [
      { id: '3', title: '二手冰箱', price: 600, images: ['https://via.placeholder.com/200'], status: 'sold' }
    ]
  } catch (error) {
    console.error('获取失败', error)
  }
}

const handleEdit = (item) => {
  ElMessage.info('编辑功能开发中')
}

const handleDelete = async (item) => {
  try {
    await ElMessageBox.confirm('确定要删除该商品吗？', '提示', { type: 'warning' })
    ElMessage.success('删除成功')
    fetchMyItems()
  } catch {
    // 取消
  }
}

onMounted(() => {
  fetchMyItems()
})
</script>

<style scoped>
.my-items-page {
  padding: 20px 0;
  min-height: calc(100vh - 120px);
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.item-card {
  margin-bottom: 20px;
  cursor: pointer;
  position: relative;
}

.item-card.sold {
  opacity: 0.7;
}

.item-image {
  width: 100%;
  height: 150px;
  object-fit: cover;
}

.item-info {
  padding: 10px 0;
}

.item-info h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  color: #f56c6c;
  font-weight: bold;
  margin: 0 0 10px 0;
}

.actions {
  display: flex;
  gap: 10px;
}

.sold-overlay {
  position: absolute;
  top: 10px;
  right: 10px;
  background: rgba(0,0,0,0.6);
  color: white;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
}
</style>
