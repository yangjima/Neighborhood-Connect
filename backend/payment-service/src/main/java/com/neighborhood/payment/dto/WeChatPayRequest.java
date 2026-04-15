package com.neighborhood.payment.dto;

import lombok.Data;

@Data
public class WeChatPayRequest {
    private String appid;          // 小程序AppID
    private String mchid;         // 商户号
    private String description;    // 商品描述
    private String outTradeNo;    // 商户订单号
    private String notifyUrl;     // 回调地址
    private Amount amount;

    @Data
    public static class Amount {
        private int total;     // 金额（分）
        private String currency = "CNY";
    }
}
