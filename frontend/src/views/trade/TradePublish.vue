<template>
  <div class="trade-publish">
    <div class="container">
      <el-card>
        <template #header>
          <span>发布闲置</span>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="publish-form"
        >
          <el-form-item label="商品标题" prop="title">
            <el-input
              v-model="form.title"
              placeholder="例如：九成新布艺沙发"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="商品分类" prop="category">
            <el-radio-group v-model="form.category">
              <el-radio label="furniture">🛋️ 家具</el-radio>
              <el-radio label="appliance">📺 家电</el-radio>
              <el-radio label="other">📦 其他</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="新旧程度" prop="condition">
            <el-radio-group v-model="form.condition">
              <el-radio label="new">
                🆕 全新（未使用或包装未拆）
              </el-radio>
              <el-radio label="like_new">
                ⭐ 九成新（偶尔使用，功能完好）
              </el-radio>
              <el-radio label="good">
                👍 八成新（正常使用，有轻微痕迹）
              </el-radio>
              <el-radio label="fair">
                👌 七成新及以下（有明显使用痕迹）
              </el-radio>
            </el-radio-group>
          </el-form-item>

          <el-form-item label="出售价格" prop="price">
            <el-input-number
              v-model="form.price"
              :min="0"
              :step="10"
              :precision="2"
              placeholder="请输入价格"
              style="width: 100%"
            >
              <template #prefix>¥</template>
            </el-input-number>
          </el-form-item>

          <el-form-item label="原价">
            <el-input-number
              v-model="form.originalPrice"
              :min="0"
              :step="10"
              :precision="2"
              placeholder="选填，帮助买家了解性价比"
              style="width: 100%"
            >
              <template #prefix>¥</template>
            </el-input-number>
          </el-form-item>

          <el-divider content-position="left">商品图片</el-divider>

          <el-form-item label="商品图片">
            <el-upload
              v-model:file-list="form.images"
              action="/api/upload/image"
              list-type="picture-card"
              :before-upload="handleBeforeUpload"
              :on-success="handleImageSuccess"
              :on-error="handleImageError"
              :on-remove="handleImageRemove"
              :limit="9"
              accept="image/*"
            >
              <el-icon><Plus /></el-icon>
            </el-upload>
            <div class="upload-tip">
              <p>📸 建议上传清晰明亮的实物照片</p>
              <p>最多上传9张图片，支持jpg、png格式，单张不超过5MB</p>
            </div>
          </el-form-item>

          <el-divider content-position="left">商品信息</el-divider>

          <el-form-item label="商品描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="6"
              placeholder="请详细描述商品的规格、材质、使用情况等，让买家更了解商品"
              maxlength="2000"
              show-word-limit
            />
            <div class="description-tips">
              <p>💡 描述建议：</p>
              <ul>
                <li>商品的品牌、型号、规格</li>
                <li>购买时间、使用频率</li>
                <li>转让原因、优势卖点</li>
                <li>是否有配件、包装是否完整</li>
              </ul>
            </div>
          </el-form-item>

          <el-form-item label="交易方式">
            <el-checkbox-group v-model="form.tradeMethods">
              <el-checkbox label="线下">🏠 当面交易</el-checkbox>
              <el-checkbox label="线上">💳 在线交易（平台担保）</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-form-item label="所在地区" prop="location">
            <el-input
              v-model="form.location"
              placeholder="例如：北京市朝阳区望京街道"
            />
          </el-form-item>

          <el-form-item label="联系方式" prop="contact">
            <el-input
              v-model="form.contact"
              placeholder="请输入联系方式（手机号或微信）"
              maxlength="50"
            />
          </el-form-item>

          <el-divider />

          <el-form-item>
            <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
              立即发布
            </el-button>
            <el-button size="large" @click="handleSaveDraft">保存草稿</el-button>
            <el-button size="large" @click="handlePreview">预览</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 预览对话框 -->
      <el-dialog v-model="showPreview" title="商品预览" width="600px">
        <div class="preview-content" v-if="form.title">
          <div class="preview-images" v-if="form.images.length">
            <img :src="form.images[0].url" class="preview-main-image" />
            <div class="preview-thumbnails">
              <img
                v-for="(img, index) in form.images.slice(1, 5)"
                :key="index"
                :src="img.url"
                class="preview-thumb"
              />
            </div>
          </div>
          <h2>{{ form.title }}</h2>
          <p class="preview-price">¥{{ form.price }}</p>
          <p class="preview-original" v-if="form.originalPrice">
            原价：¥{{ form.originalPrice }}
          </p>
          <div class="preview-tags">
            <el-tag>{{ getCategoryName(form.category) }}</el-tag>
            <el-tag type="success">{{ getConditionName(form.condition) }}</el-tag>
          </div>
          <p class="preview-location">📍 {{ form.location }}</p>
          <p class="preview-desc">{{ form.description || '暂无描述' }}</p>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { tradeApi } from '../../api/trade'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const showPreview = ref(false)

const form = reactive({
  title: '',
  category: 'furniture',
  condition: 'like_new',
  price: 0,
  originalPrice: 0,
  images: [],
  description: '',
  tradeMethods: ['线下'],
  location: '',
  contact: ''
})

const rules = {
  title: [{ required: true, message: '请输入商品标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择商品分类', trigger: 'change' }],
  condition: [{ required: true, message: '请选择新旧程度', trigger: 'change' }],
  price: [{ required: true, message: '请输入出售价格', trigger: 'blur' }],
  description: [{ required: true, message: '请输入商品描述', trigger: 'blur' }],
  location: [{ required: true, message: '请输入所在地区', trigger: 'blur' }],
  contact: [{ required: true, message: '请输入联系方式', trigger: 'blur' }]
}

const getCategoryName = (category) => {
  const categories = { furniture: '家具', appliance: '家电', other: '其他' }
  return categories[category] || category
}

const getConditionName = (condition) => {
  const conditions = { new: '全新', like_new: '九成新', good: '八成新', fair: '七成新及以下' }
  return conditions[condition] || condition
}

const handleBeforeUpload = (file) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过5MB')
    return false
  }
  return true
}

const handleImageSuccess = (response, file) => {
  form.images.push({
    name: file.name,
    url: response.url || URL.createObjectURL(file.raw)
  })
  ElMessage.success('图片上传成功')
}

const handleImageError = () => {
  ElMessage.error('图片上传失败')
}

const handleImageRemove = (file, fileList) => {
  form.images = fileList
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    if (form.images.length === 0) {
      ElMessage.warning('请至少上传一张商品图片')
      return
    }

    submitting.value = true
    try {
      const imageUrls = form.images.map(img => img.url)
      const data = {
        ...form,
        images: imageUrls
      }

      const response = await tradeApi.publish(data)
      ElMessage.success('发布成功！')

      // 清除草稿
      localStorage.removeItem('trade_draft')

      setTimeout(() => {
        router.push(`/trade/${response.id}`)
      }, 1500)
    } catch (error) {
      ElMessage.error('发布失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

const handleSaveDraft = () => {
  localStorage.setItem('trade_draft', JSON.stringify(form))
  ElMessage.success('草稿已保存')
}

const handlePreview = () => {
  showPreview.value = true
}

// 加载草稿
const loadDraft = () => {
  const draft = localStorage.getItem('trade_draft')
  if (draft) {
    try {
      const parsed = JSON.parse(draft)
      Object.assign(form, parsed)
    } catch {
      // ignore
    }
  }
}

loadDraft()
</script>

<style scoped>
.trade-publish {
  min-height: calc(100vh - 120px);
  background-color: #f5f5f5;
  padding: 20px 0;
}

.container {
  max-width: 900px;
  margin: 0 auto;
  padding: 0 20px;
}

.publish-form {
  padding: 20px;
}

.upload-tip {
  color: #999;
  font-size: 12px;
  margin-top: 8px;
}

.description-tips {
  margin-top: 10px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  font-size: 12px;
  color: #666;
}

.description-tips p {
  margin: 0 0 8px 0;
}

.description-tips ul {
  margin: 0;
  padding-left: 20px;
}

.description-tips li {
  margin-bottom: 4px;
}

.preview-content {
  padding: 20px;
}

.preview-images {
  margin-bottom: 20px;
}

.preview-main-image {
  width: 100%;
  height: 300px;
  object-fit: cover;
  border-radius: 8px;
}

.preview-thumbnails {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.preview-thumb {
  width: 80px;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
}

.preview-content h2 {
  margin-bottom: 10px;
}

.preview-price {
  font-size: 28px;
  color: #f56c6c;
  font-weight: bold;
  margin: 10px 0;
}

.preview-original {
  color: #999;
  text-decoration: line-through;
  margin: 5px 0;
}

.preview-tags {
  margin: 15px 0;
  display: flex;
  gap: 10px;
}

.preview-location {
  color: #666;
  margin: 10px 0;
}

.preview-desc {
  color: #333;
  line-height: 1.6;
  white-space: pre-wrap;
}
</style>
