package com.neighborhood.payment.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Positive;
import lombok.Data;
import java.math.BigDecimal;

@Data
public class CreatePaymentRequest {
    @NotBlank(message = "订单ID不能为空")
    private String orderId;

    @NotNull(message = "金额不能为空")
    @Positive(message = "金额必须大于0")
    private BigDecimal amount;

    @NotBlank(message = "支付方式不能为空")
    private String paymentMethod; // wechat, alipay

    private String returnUrl;
}
