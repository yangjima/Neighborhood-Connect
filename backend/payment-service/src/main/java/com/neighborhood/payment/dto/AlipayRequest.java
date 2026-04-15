package com.neighborhood.payment.dto;

import lombok.Data;

@Data
public class AlipayRequest {
    private String outTradeNo;     // 商户订单号
    private String totalAmount;    // 金额
    private String subject;        // 订单标题
    private String body;          // 订单描述
    private String returnUrl;     // 回调地址
}
