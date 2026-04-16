<template>
  <div class="smart-search-bar">
    <el-input
      v-model="query"
      placeholder="试试输入: 望京3000左右的两室一厅"
      @keyup.enter="handleSearch"
      :loading="loading"
      size="large"
      clearable
    >
      <template #append>
        <el-button
          @click="handleSearch"
          :loading="loading"
          type="primary"
        >
          <el-icon><Search /></el-icon>
          搜索
        </el-button>
      </template>
    </el-input>

    <!-- Query understanding -->
    <div v-if="queryUnderstanding" class="query-understanding">
      <el-tag type="success" size="large">
        <el-icon><Check /></el-icon>
        {{ queryUnderstanding }}
      </el-tag>
    </div>

    <!-- Applied filters -->
    <div v-if="appliedFilters && Object.keys(appliedFilters).length > 0" class="applied-filters">
      <span class="filter-label">筛选条件:</span>
      <el-tag
        v-for="(value, key) in appliedFilters"
        :key="key"
        closable
        @close="removeFilter(key)"
        class="filter-tag"
      >
        {{ formatFilter(key, value) }}
      </el-tag>
    </div>

    <!-- Error message -->
    <el-alert
      v-if="errorMessage"
      :title="errorMessage"
      type="error"
      :closable="true"
      @close="errorMessage = ''"
      class="error-alert"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Search, Check } from '@element-plus/icons-vue'
import { smartSearchApi } from '@/api/ai'
import { ElMessage } from 'element-plus'

const props = defineProps({
  context: {
    type: String,
    required: true,
    validator: (value) => ['rental', 'trade'].includes(value)
  }
})

const emit = defineEmits(['search-results'])

const query = ref('')
const loading = ref(false)
const queryUnderstanding = ref('')
const appliedFilters = ref(null)
const errorMessage = ref('')

const handleSearch = async () => {
  if (!query.value.trim()) {
    ElMessage.warning('请输入搜索内容')
    return
  }

  loading.value = true
  errorMessage.value = ''

  try {
    const response = await smartSearchApi.search({
      query: query.value,
      context: props.context
    })

    if (response.success) {
      queryUnderstanding.value = response.query_understanding
      appliedFilters.value = response.applied_filters

      // Emit results to parent
      emit('search-results', {
        data: response.data,
        total: response.total
      })

      if (response.data.length === 0) {
        ElMessage.info('未找到匹配结果，试试调整搜索条件')
      }
    } else {
      errorMessage.value = response.error || '搜索失败'
    }
  } catch (error) {
    console.error('Search failed:', error)
    errorMessage.value = '搜索服务暂时不可用，请稍后重试'
  } finally {
    loading.value = false
  }
}

const removeFilter = (key) => {
  if (appliedFilters.value) {
    delete appliedFilters.value[key]
    // Re-trigger search without this filter
    handleSearch()
  }
}

const formatFilter = (key, value) => {
  const filterMap = {
    location: `位置: ${value}`,
    min_price: `最低价: ${value}元`,
    max_price: `最高价: ${value}元`,
    type: `类型: ${value}`,
    category: `分类: ${value}`,
    condition: `成色: ${value}`
  }
  return filterMap[key] || `${key}: ${value}`
}
</script>

<style scoped>
.smart-search-bar {
  margin-bottom: 20px;
}

.query-understanding {
  margin-top: 12px;
}

.applied-filters {
  margin-top: 12px;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label {
  font-size: 14px;
  color: #606266;
  margin-right: 8px;
}

.filter-tag {
  margin: 0;
}

.error-alert {
  margin-top: 12px;
}
</style>
