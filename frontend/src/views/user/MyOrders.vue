<template>
  <div class="my-orders-page">
    <div class="container">
      <el-card>
        <template #header>
          <span>我的订单</span>
        </template>

        <el-tabs v-model="activeTab">
          <el-tab-pane label="全部订单" name="all">
            <el-table :data="orders" stripe>
              <el-table-column prop="orderId" label="订单号" width="180" />
              <el-table-column label="商品" min-width="200">
                <template #default="{ row }">
                  <div class="order-item">
                    <img :src="row.itemImage" class="item-thumb" />
                    <span>{{ row.itemTitle }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="price" label="金额" width="100">
                <template #default="{ row }">
                  <span class="price">¥{{ row.price }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="status" label="状态" width="100">
                <template #default="{ row }">
                  <el-tag :type="getStatusType(row.status)">
                    {{ getStatusName(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="createdAt" label="下单时间" width="120" />
              <el-table-column label="操作" width="150">
                <template #default="{ row }">
                  <el-button
                    v-if="row.status === 'pending'"
                    type="primary"
                    size="small"
                    @click="handlePay(row)"
                  >
                    去支付
                  </el-button>
                  <el-button
                    v-if="row.status === 'paid'"
                    type="success"
                    size="small"
                    @click="handleConfirm(row)"
                  >
                    确认收货
                  </el-button>
                  <el-button
                    v-if="row.status === 'pending'"
                    type="danger"
                    size="small"
                    @click="handleCancel(row)"
                  >
                    取消
                  </el-button>
                </template>
              </el-table-column>
            </el-table>

            <el-empty v-if="!orders.length" description="暂无订单" />
          </el-tab-pane>

          <el-tab-pane label="待支付" name="pending">
            <el-empty description="暂无待支付订单" />
          </el-tab-pane>

          <el-tab-pane label="已完成" name="completed">
            <el-empty description="暂无已完成订单" />
          </el-tab-pane>
        </el-tabs>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

const activeTab = ref('all')

const orders = ref([
  {
    orderId: 'ORD202401150001',
    itemTitle: '九成新沙发',
    itemImage: 'https://via.placeholder.com/50',
    price: 800,
    status: 'pending',
    createdAt: '2024-01-15'
  },
  {
    orderId: 'ORD202401100002',
    itemTitle: '宜家书桌',
    itemImage: 'https://via.placeholder.com/50',
    price: 300,
    status: 'paid',
    createdAt: '2024-01-10'
  }
])

const getStatusName = (status) => {
  const names = {
    pending: '待支付',
    paid: '已支付',
    shipped: '已发货',
    completed: '已完成',
    cancelled: '已取消'
  }
  return names[status] || status
}

const getStatusType = (status) => {
  const types = {
    pending: 'warning',
    paid: 'primary',
    shipped: 'info',
    completed: 'success',
    cancelled: 'info'
  }
  return types[status] || 'info'
}

const handlePay = (order) => {
  ElMessage.info('支付功能开发中')
}

const handleConfirm = (order) => {
  ElMessage.success('确认收货成功')
}

const handleCancel = (order) => {
  ElMessage.info('取消订单')
}
</script>

<style scoped>
.my-orders-page {
  padding: 20px 0;
  min-height: calc(100vh - 120px);
  background-color: #f5f5f5;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.order-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.item-thumb {
  width: 50px;
  height: 50px;
  object-fit: cover;
  border-radius: 4px;
}

.price {
  color: #f56c6c;
  font-weight: bold;
}
</style>
