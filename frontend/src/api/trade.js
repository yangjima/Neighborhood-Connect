import { tradeRequest } from '../utils/request'

export const tradeApi = {
  // 获取商品列表
  getList(params) {
    return tradeRequest.get('/api/trade/list', { params })
  },

  // 获取商品详情
  getDetail(id) {
    return tradeRequest.get(`/api/trade/${id}`)
  },

  // 发布商品
  publish(data) {
    return tradeRequest.post('/api/trade/publish', data)
  },

  // 搜索商品
  search(params) {
    return tradeRequest.get('/api/trade/search', { params })
  },

  // 创建订单
  createOrder(itemId) {
    return tradeRequest.post('/api/trade/order', { item_id: itemId })
  }
}
