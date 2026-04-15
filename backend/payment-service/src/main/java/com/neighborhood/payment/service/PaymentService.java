package com.neighborhood.payment.service;

import com.neighborhood.payment.dto.*;
import com.neighborhood.payment.entity.Payment;
import com.neighborhood.payment.repository.PaymentRepository;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.gson.Gson;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.HashMap;
import java.util.Map;
import java.util.UUID;

@Slf4j
@Service
public class PaymentService {

    @Autowired
    private PaymentRepository paymentRepository;

    @Autowired
    private StringRedisTemplate redisTemplate;

    @Value("${wechat.mchid:}")
    private String wechatMchId;

    @Value("${wechat.appid:}")
    private String wechatAppId;

    @Value("${alipay.appId:}")
    private String alipayAppId;

    @Value("${alipay.privateKey:}")
    private String alipayPrivateKey;

    @Value("${alipay.alipayPublicKey:}")
    private String alipayPublicKey;

    @Value("${payment.callback-url:http://localhost}")
    private String callbackUrl;

    private final ObjectMapper objectMapper = new ObjectMapper();
    private final Gson gson = new Gson();

    @Transactional
    public PaymentResponse createPayment(CreatePaymentRequest request, Long userId) {
        // 检查订单是否已支付
        Payment existingPayment = paymentRepository.findByOrderId(request.getOrderId());
        if (existingPayment != null && "paid".equals(existingPayment.getStatus())) {
            throw new RuntimeException("订单已支付");
        }

        // 生成支付记录
        Payment payment = new Payment();
        payment.setOrderId(request.getOrderId());
        payment.setUserId(userId);
        payment.setAmount(request.getAmount());
        payment.setPaymentMethod(request.getPaymentMethod());
        payment.setStatus("pending");
        payment.setCreatedAt(LocalDateTime.now());
        payment.setUpdatedAt(LocalDateTime.now());

        payment = paymentRepository.save(payment);

        Map<String, Object> paymentData = new HashMap<>();
        paymentData.put("paymentId", String.valueOf(payment.getId()));
        paymentData.put("orderId", request.getOrderId());

        String qrCode = null;

        try {
            if ("wechat".equals(request.getPaymentMethod())) {
                // 微信支付
                Map<String, Object> wechatData = createWeChatPay(request, payment);
                paymentData.putAll(wechatData);
            } else if ("alipay".equals(request.getPaymentMethod())) {
                // 支付宝支付
                String formData = createAlipayTrade(request, payment);
                paymentData.put("formData", formData);
                qrCode = formData;
            }
        } catch (Exception e) {
            log.error("创建支付失败", e);
            // 使用沙箱模式返回模拟数据
            paymentData.put("sandbox", true);
            paymentData.put("mockOrderId", "MOCK_" + System.currentTimeMillis());
        }

        return new PaymentResponse(
                String.valueOf(payment.getId()),
                request.getOrderId(),
                request.getPaymentMethod(),
                "pending",
                paymentData,
                qrCode
        );
    }

    private Map<String, Object> createWeChatPay(CreatePaymentRequest request, Payment payment) {
        Map<String, Object> data = new HashMap<>();
        data.put("appid", wechatAppId);
        data.put("mchid", wechatMchId);
        data.put("description", "邻里通订单-" + request.getOrderId());
        data.put("out_trade_no", request.getOrderId());
        data.put("notify_url", callbackUrl + "/api/payment/notify/wechat");
        data.put("amount", Map.of(
                "total", request.getAmount().multiply(new BigDecimal("100")).intValue(),
                "currency", "CNY"
        ));
        return data;
    }

    private String createAlipayTrade(CreatePaymentRequest request, Payment payment) {
        // 实际需要调用支付宝SDK
        // 这里返回模拟的表单数据
        return "<form>Alipay Sandbox Payment</form>";
    }

    public void handleWeChatNotify(String notifyData) {
        try {
            // 实际需要验证签名
            Map<String, Object> data = gson.fromJson(notifyData, Map.class);
            String outTradeNo = (String) data.get("out_trade_no");
            String transactionId = (String) data.get("transaction_id");

            Payment payment = paymentRepository.findByOrderId(outTradeNo);
            if (payment != null) {
                payment.setStatus("paid");
                payment.setTransactionId(transactionId);
                payment.setPaymentTime(LocalDateTime.now());
                payment.setNotifyData(notifyData);
                payment.setUpdatedAt(LocalDateTime.now());
                paymentRepository.save(payment);

                // 通知其他服务订单已支付
                notifyOrderService(payment);
            }
        } catch (Exception e) {
            log.error("处理微信支付回调失败", e);
            throw new RuntimeException("处理失败");
        }
    }

    public void handleAlipayNotify(String notifyData) {
        try {
            Map<String, Object> params = new HashMap<>();
            // 解析支付宝回调参数

            String outTradeNo = (String) params.get("out_trade_no");
            String tradeNo = (String) params.get("trade_no");
            String tradeStatus = (String) params.get("trade_status");

            if ("TRADE_SUCCESS".equals(tradeStatus) || "TRADE_FINISHED".equals(tradeStatus)) {
                Payment payment = paymentRepository.findByOrderId(outTradeNo);
                if (payment != null) {
                    payment.setStatus("paid");
                    payment.setTransactionId(tradeNo);
                    payment.setPaymentTime(LocalDateTime.now());
                    payment.setNotifyData(notifyData);
                    payment.setUpdatedAt(LocalDateTime.now());
                    paymentRepository.save(payment);

                    notifyOrderService(payment);
                }
            }
        } catch (Exception e) {
            log.error("处理支付宝回调失败", e);
            throw new RuntimeException("处理失败");
        }
    }

    private void notifyOrderService(Payment payment) {
        // 通过消息队列通知订单服务更新状态
        // 或者直接调用订单服务API
        log.info("订单 {} 支付成功，通知下游服务", payment.getOrderId());
    }

    public PaymentResponse queryPayment(String orderId) {
        Payment payment = paymentRepository.findByOrderId(orderId);
        if (payment == null) {
            return null;
        }

        return new PaymentResponse(
                String.valueOf(payment.getId()),
                payment.getOrderId(),
                payment.getPaymentMethod(),
                payment.getStatus(),
                null,
                null
        );
    }

    @Transactional
    public boolean refund(String orderId, BigDecimal amount) {
        Payment payment = paymentRepository.findByOrderId(orderId);
        if (payment == null || !"paid".equals(payment.getStatus())) {
            return false;
        }

        // 调用支付渠道退款
        if ("wechat".equals(payment.getPaymentMethod())) {
            // 微信退款
        } else if ("alipay".equals(payment.getPaymentMethod())) {
            // 支付宝退款
        }

        payment.setStatus("refunded");
        payment.setUpdatedAt(LocalDateTime.now());
        paymentRepository.save(payment);

        return true;
    }
}
