<template>
  <div class="rental-publish">
    <div class="container">
      <el-card>
        <template #header>
          <span>发布房源</span>
        </template>

        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          label-width="100px"
          class="publish-form"
        >
          <el-form-item label="房源标题" prop="title">
            <el-input
              v-model="form.title"
              placeholder="例如：精装两室一厅出租"
              maxlength="50"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="租赁方式" prop="type">
            <el-radio-group v-model="form.type">
              <el-radio label="whole">整租</el-radio>
              <el-radio label="shared">合租</el-radio>
              <el-radio label="single">单间</el-radio>
            </el-radio-group>
          </el-form-item>

          <el-row :gutter="20">
            <el-col :span="12">
              <el-form-item label="月租金(元)" prop="price">
                <el-input-number
                  v-model="form.price"
                  :min="0"
                  :step="100"
                  :precision="2"
                  placeholder="请输入租金"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="面积(m²)" prop="area">
                <el-input-number
                  v-model="form.area"
                  :min="0"
                  :step="1"
                  :precision="1"
                  placeholder="请输入面积"
                  style="width: 100%"
                />
              </el-form-item>
            </el-col>
          </el-row>

          <el-divider content-position="left">位置信息</el-divider>

          <el-form-item label="小区名称" prop="location.community">
            <el-input
              v-model="form.location.community"
              placeholder="请输入小区名称"
            />
          </el-form-item>

          <el-form-item label="详细地址" prop="location.address">
            <el-input
              v-model="form.location.address"
              placeholder="请输入详细地址"
            />
          </el-form-item>

          <el-divider content-position="left">房屋配置</el-divider>

          <el-form-item label="设施配置">
            <el-checkbox-group v-model="form.facilities">
              <el-checkbox label="空调">❄️ 空调</el-checkbox>
              <el-checkbox label="冰箱">🧊 冰箱</el-checkbox>
              <el-checkbox label="洗衣机">👕 洗衣机</el-checkbox>
              <el-checkbox label="热水器">🚿 热水器</el-checkbox>
              <el-checkbox label="床">🛏️ 床</el-checkbox>
              <el-checkbox label="沙发">🛋️ 沙发</el-checkbox>
              <el-checkbox label="电视">📺 电视</el-checkbox>
              <el-checkbox label="网络">📶 网络</el-checkbox>
              <el-checkbox label="暖气">🔥 暖气</el-checkbox>
              <el-checkbox label="衣柜">🗄️ 衣柜</el-checkbox>
              <el-checkbox label="厨房">🍳 厨房</el-checkbox>
              <el-checkbox label="卫生间">🚽 卫生间</el-checkbox>
            </el-checkbox-group>
          </el-form-item>

          <el-divider content-position="left">房源图片</el-divider>

          <el-form-item label="房源图片">
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
              最多上传9张图片，支持jpg、png格式，单张不超过5MB
            </div>
          </el-form-item>

          <el-divider content-position="left">详细信息</el-divider>

          <el-form-item label="房源描述" prop="description">
            <el-input
              v-model="form.description"
              type="textarea"
              :rows="6"
              placeholder="请详细描述房屋情况、交通便利程度、周边配套等"
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>

          <el-form-item label="联系电话" prop="contact">
            <el-input
              v-model="form.contact"
              placeholder="请输入联系电话"
              maxlength="20"
            />
          </el-form-item>

          <el-form-item>
            <el-button type="primary" size="large" :loading="submitting" @click="handleSubmit">
              发布房源
            </el-button>
            <el-button size="large" @click="handleSaveDraft">保存草稿</el-button>
            <el-button size="large" @click="handlePreview">预览</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- 预览对话框 -->
      <el-dialog v-model="showPreview" title="房源预览" width="800px">
        <div class="preview-content">
          <h2>{{ form.title }}</h2>
          <p class="preview-price">¥{{ form.price }}/月</p>
          <p>{{ form.type === 'whole' ? '整租' : form.type === 'shared' ? '合租' : '单间' }}</p>
          <p>面积：{{ form.area }}m²</p>
          <p>位置：{{ form.location.community }} - {{ form.location.address }}</p>
          <p>配置：{{ form.facilities.join('、') || '暂无' }}</p>
          <p>描述：{{ form.description || '暂无' }}</p>
        </div>
      </el-dialog>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { rentalApi } from '../../api/rental'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'

const router = useRouter()
const formRef = ref(null)
const submitting = ref(false)
const showPreview = ref(false)

const form = reactive({
  title: '',
  type: 'whole',
  price: 0,
  area: 0,
  location: {
    community: '',
    address: '',
    coordinates: []
  },
  facilities: [],
  images: [],
  description: '',
  contact: ''
})

const rules = {
  title: [{ required: true, message: '请输入房源标题', trigger: 'blur' }],
  type: [{ required: true, message: '请选择租赁方式', trigger: 'change' }],
  price: [{ required: true, message: '请输入租金', trigger: 'blur' }],
  area: [{ required: true, message: '请输入面积', trigger: 'blur' }],
  'location.community': [{ required: true, message: '请输入小区名称', trigger: 'blur' }],
  'location.address': [{ required: true, message: '请输入详细地址', trigger: 'blur' }],
  description: [{ required: true, message: '请输入房源描述', trigger: 'blur' }],
  contact: [
    { required: true, message: '请输入联系电话', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '请输入正确的手机号', trigger: 'blur' }
  ]
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
  // 假设返回 { url: '...' }
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

    submitting.value = true
    try {
      const imageUrls = form.images.map(img => img.url)
      const data = {
        ...form,
        images: imageUrls
      }

      const response = await rentalApi.publish(data)
      ElMessage.success('发布成功！')

      // 跳转到房源详情页
      setTimeout(() => {
        router.push(`/rental/${response.id}`)
      }, 1500)
    } catch (error) {
      ElMessage.error('发布失败，请稍后重试')
    } finally {
      submitting.value = false
    }
  })
}

const handleSaveDraft = () => {
  localStorage.setItem('rental_draft', JSON.stringify(form))
  ElMessage.success('草稿已保存')
}

const handlePreview = () => {
  showPreview.value = true
}

// 加载草稿
const loadDraft = () => {
  const draft = localStorage.getItem('rental_draft')
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
.rental-publish {
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

.preview-content {
  padding: 20px;
}

.preview-content h2 {
  margin-bottom: 15px;
}

.preview-price {
  font-size: 24px;
  color: #f56c6c;
  font-weight: bold;
  margin: 10px 0;
}

.preview-content p {
  margin: 8px 0;
  color: #666;
}
</style>
