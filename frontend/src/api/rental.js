import { rentalRequest } from '../utils/request'

export const rentalApi = {
  // 获取房源列表
  getList(params) {
    return rentalRequest.get('/api/rental/list', { params })
  },

  // 获取房源详情
  getDetail(id) {
    return rentalRequest.get(`/api/rental/${id}`)
  },

  // 发布房源
  publish(data) {
    return rentalRequest.post('/api/rental/publish', data)
  },

  // 搜索房源
  search(params) {
    return rentalRequest.get('/api/rental/search', { params })
  },

  // 收藏房源
  favorite(id) {
    return rentalRequest.post('/api/rental/favorite', { rental_id: id })
  }
}
