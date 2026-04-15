import axios from 'axios'
import { useUserStore } from '../store/user'

// 创建一个axios实例用于每个服务
const createRequest = (baseURL) => {
  const instance = axios.create({
    baseURL,
    timeout: 10000
  })

  instance.interceptors.request.use(
    config => {
      const userStore = useUserStore()
      if (userStore.token) {
        config.headers.Authorization = `Bearer ${userStore.token}`
        config.headers['X-User-Id'] = userStore.userInfo?.userId || ''
      }
      return config
    },
    error => Promise.reject(error)
  )

  instance.interceptors.response.use(
    response => response.data,
    error => {
      if (error.response?.status === 401) {
        const userStore = useUserStore()
        userStore.logout()
        window.location.href = '/user/login'
      }
      return Promise.reject(error)
    }
  )

  return instance
}

// 导出不同的API实例
const rentalRequest = createRequest('http://localhost:8001')
const tradeRequest = createRequest('http://localhost:8002')
const userRequest = createRequest('http://localhost:8081')
const uploadRequest = createRequest('http://localhost:8004')

export { rentalRequest, tradeRequest, userRequest, uploadRequest }
export default createRequest('http://localhost:8001')
