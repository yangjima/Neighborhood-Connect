import { userRequest } from '../utils/request'

export const authApi = {
  // 用户登录
  login(data) {
    return userRequest.post('/api/user/login', data)
  },

  // 用户注册
  register(data) {
    return userRequest.post('/api/user/register', data)
  },

  // 获取用户信息
  getProfile() {
    return userRequest.get('/api/user/profile')
  },

  // 发送验证码
  sendCode(phone) {
    return userRequest.post('/api/user/send-code', { phone })
  },

  // 修改密码
  changePassword(data) {
    return userRequest.post('/api/user/change-password', data)
  },

  // 退出登录
  logout() {
    return userRequest.post('/api/user/logout')
  }
}
