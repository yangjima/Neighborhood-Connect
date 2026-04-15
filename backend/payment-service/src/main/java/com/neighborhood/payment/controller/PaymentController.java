package com.neighborhood.payment.controller;

import com.neighborhood.payment.dto.*;
import com.neighborhood.payment.service.PaymentService;
import jakarta.validation.Valid;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@Slf4j
@RestController
@RequestMapping("/api/payment")
public class PaymentController {

    @Autowired
    private PaymentService paymentService;

    @PostMapping("/create")
    public ResponseEntity<?> createPayment(
            @Valid @RequestBody CreatePaymentRequest request,
            @RequestHeader(value = "X-User-Id", required = false) Long userId
    ) {
        try {
            if (userId == null) {
                userId = 1L; // 默认用户ID（开发环境）
            }

            PaymentResponse response = paymentService.createPayment(request, userId);
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            log.error("创建支付失败", e);
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }

    @PostMapping("/notify/wechat")
    public ResponseEntity<?> wechatNotify(@RequestBody String notifyData) {
        try {
            paymentService.handleWeChatNotify(notifyData);
            return ResponseEntity.ok().body("<xml><return_code><![CDATA[SUCCESS]]></return_code></xml>");
        } catch (Exception e) {
            log.error("微信支付回调处理失败", e);
            return ResponseEntity.ok().body("<xml><return_code><![CDATA[FAIL]]></return_code></xml>");
        }
    }

    @PostMapping("/notify/alipay")
    public ResponseEntity<?> alipayNotify(@RequestParam Map<String, String> params) {
        try {
            paymentService.handleAlipayNotify(params.toString());
            return ResponseEntity.ok("success");
        } catch (Exception e) {
            log.error("支付宝回调处理失败", e);
            return ResponseEntity.ok("fail");
        }
    }

    @GetMapping("/query/{orderId}")
    public ResponseEntity<?> queryPayment(@PathVariable String orderId) {
        PaymentResponse response = paymentService.queryPayment(orderId);
        if (response == null) {
            return ResponseEntity.notFound().build();
        }
        return ResponseEntity.ok(response);
    }

    @PostMapping("/refund")
    public ResponseEntity<?> refund(@RequestBody Map<String, Object> request) {
        String orderId = (String) request.get("orderId");
        if (orderId == null) {
            return ResponseEntity.badRequest().body(Map.of("message", "订单ID不能为空"));
        }

        try {
            java.math.BigDecimal amount = new java.math.BigDecimal(request.getOrDefault("amount", "0").toString());
            boolean success = paymentService.refund(orderId, amount);
            if (success) {
                return ResponseEntity.ok(Map.of("message", "退款成功"));
            } else {
                return ResponseEntity.badRequest().body(Map.of("message", "退款失败"));
            }
        } catch (Exception e) {
            return ResponseEntity.badRequest().body(Map.of("message", e.getMessage()));
        }
    }
}
