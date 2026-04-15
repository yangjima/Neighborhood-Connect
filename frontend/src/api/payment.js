import request from '../utils/request'

export const paymentApi = {
  // 创建支付订单
  createPayment(data) {
    return request.post('/api/payment/create', data)
  },

  // 查询支付状态
  queryPayment(orderId) {
    return request.get(`/api/payment/query/${orderId}`)
  },

  // 申请退款
  refund(orderId, amount) {
    return request.post('/api/payment/refund', { orderId, amount })
  },

  // 微信H5调起支付参数
  getWeChatParams(orderId) {
    return request.get(`/api/payment/wechat/params/${orderId}`)
  },

  // 支付宝支付参数
  getAlipayParams(orderId) {
    return request.get(`/api/payment/alipay/params/${orderId}`)
  }
}
