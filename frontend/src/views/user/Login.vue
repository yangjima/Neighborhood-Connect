<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h1>邻里通</h1>
        <p>连接社区，服务生活</p>
      </div>

      <el-tabs v-model="activeTab" class="login-tabs">
        <el-tab-pane label="登录" name="login">
          <el-form
            ref="loginFormRef"
            :model="loginForm"
            :rules="loginRules"
            class="login-form"
          >
            <el-form-item prop="phone">
              <el-input
                v-model="loginForm.phone"
                placeholder="请输入手机号"
                prefix-icon="Phone"
                size="large"
              />
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="loginForm.password"
                type="password"
                placeholder="请输入密码"
                prefix-icon="Lock"
                size="large"
                show-password
                @keyup.enter="handleLogin"
              />
            </el-form-item>

            <el-form-item>
              <div class="form-options">
                <el-checkbox v-model="rememberMe">记住我</el-checkbox>
                <el-link type="primary" @click="showResetDialog = true">忘记密码？</el-link>
              </div>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-button"
                @click="handleLogin"
              >
                登录
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="注册" name="register">
          <el-form
            ref="registerFormRef"
            :model="registerForm"
            :rules="registerRules"
            class="login-form"
          >
            <el-form-item prop="phone">
              <el-input
                v-model="registerForm.phone"
                placeholder="请输入手机号"
                prefix-icon="Phone"
                size="large"
              />
            </el-form-item>

            <el-form-item prop="code">
              <div class="code-input">
                <el-input
                  v-model="registerForm.code"
                  placeholder="请输入验证码"
                  prefix-icon="Key"
                  size="large"
                />
                <el-button
                  :disabled="codeSent"
                  @click="handleSendCode"
                >
                  {{ codeSent ? `${countdown}s后重发` : '获取验证码' }}
                </el-button>
              </div>
            </el-form-item>

            <el-form-item prop="password">
              <el-input
                v-model="registerForm.password"
                type="password"
                placeholder="请设置密码（6位以上）"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item prop="confirmPassword">
              <el-input
                v-model="registerForm.confirmPassword"
                type="password"
                placeholder="请确认密码"
                prefix-icon="Lock"
                size="large"
                show-password
              />
            </el-form-item>

            <el-form-item prop="userType">
              <el-radio-group v-model="registerForm.userType" size="large">
                <el-radio-button label="resident">我是居民</el-radio-button>
                <el-radio-button label="merchant">我是商家</el-radio-button>
                <el-radio-button label="property">我是物业</el-radio-button>
              </el-radio-group>
            </el-form-item>

            <el-form-item>
              <el-button
                type="primary"
                size="large"
                :loading="loading"
                class="login-button"
                @click="handleRegister"
              >
                注册
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '../store/user'
import { ElMessage } from 'element-plus'
import { authApi } from '../api/auth'

const router = useRouter()
const userStore = useUserStore()

const activeTab = ref('login')
const loading = ref(false)
const rememberMe = ref(false)
const showResetDialog = ref(false)
const codeSent = ref(false)
const countdown = ref(60)

const loginFormRef = ref(null)
const registerFormRef = ref(null)

const loginForm = reactive({
  phone: '',
  password: ''
})

const registerForm = reactive({
  phone: '',
  code: '',
  password: '',
  confirmPassword: '',
  userType: 'resident'
})

// 表单验证规则
const validatePhone = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入手机号'))
  } else if (!/^1[3-9]\d{9}$/.test(value)) {
    callback(new Error('请输入正确的手机号'))
  } else {
    callback()
  }
}

const validatePassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入密码'))
  } else if (value.length < 6) {
    callback(new Error('密码不能少于6位'))
  } else {
    callback()
  }
}

const validateConfirmPassword = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请确认密码'))
  } else if (value !== registerForm.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const validateCode = (rule, value, callback) => {
  if (!value) {
    callback(new Error('请输入验证码'))
  } else if (!/^\d{4,6}$/.test(value)) {
    callback(new Error('请输入4-6位数字验证码'))
  } else {
    callback()
  }
}

const loginRules = {
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }]
}

const registerRules = {
  phone: [{ validator: validatePhone, trigger: 'blur' }],
  code: [{ validator: validateCode, trigger: 'blur' }],
  password: [{ validator: validatePassword, trigger: 'blur' }],
  confirmPassword: [{ validator: validateConfirmPassword, trigger: 'blur' }]
}

// 发送验证码
const handleSendCode = async () => {
  if (!registerForm.phone || !/^1[3-9]\d{9}$/.test(registerForm.phone)) {
    ElMessage.warning('请输入正确的手机号')
    return
  }

  try {
    await authApi.sendCode(registerForm.phone)
    ElMessage.success('验证码已发送')

    codeSent.value = true
    countdown.value = 60
    const timer = setInterval(() => {
      countdown.value--
      if (countdown.value <= 0) {
        codeSent.value = false
        clearInterval(timer)
      }
    }, 1000)
  } catch (error) {
    ElMessage.error('发送验证码失败')
  }
}

// 登录
const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      const response = await authApi.login(loginForm)
      userStore.setToken(response.token)
      userStore.setUserInfo({
        userId: response.userId,
        nickname: response.nickname,
        userType: response.userType
      })

      ElMessage.success('登录成功')
      router.push('/')
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '登录失败')
    } finally {
      loading.value = false
    }
  })
}

// 注册
const handleRegister = async () => {
  if (!registerFormRef.value) return

  await registerFormRef.value.validate(async (valid) => {
    if (!valid) return

    loading.value = true
    try {
      await authApi.register(registerForm)
      ElMessage.success('注册成功，请登录')

      activeTab.value = 'login'
      loginForm.phone = registerForm.phone
    } catch (error) {
      ElMessage.error(error.response?.data?.message || '注册失败')
    } finally {
      loading.value = false
    }
  })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.login-box {
  width: 420px;
  padding: 40px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 30px;
}

.login-header h1 {
  font-size: 32px;
  color: #333;
  margin-bottom: 10px;
}

.login-header p {
  color: #666;
  font-size: 14px;
}

.login-tabs {
  margin-bottom: 20px;
}

.login-form {
  margin-top: 20px;
}

.code-input {
  display: flex;
  gap: 10px;
  width: 100%;
}

.code-input .el-input {
  flex: 1;
}

.form-options {
  width: 100%;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.login-button {
  width: 100%;
}

:deep(.el-tabs__item) {
  font-size: 16px;
  height: 50px;
  line-height: 50px;
}

:deep(.el-tabs__item.is-active) {
  color: #409eff;
  font-weight: bold;
}

:deep(.el-tabs__active-bar) {
  height: 3px;
}
</style>
