package com.neighborhood.payment.dto;

import lombok.AllArgsConstructor;
import lombok.Data;

@Data
@AllArgsConstructor
public class PaymentResponse {
    private String paymentId;
    private String orderId;
    private String paymentMethod;
    private String status;
    private Object paymentData; // 支付参数（调起支付的必要信息）
    private String qrCode; // 二维码URL（扫码支付时使用）
}
