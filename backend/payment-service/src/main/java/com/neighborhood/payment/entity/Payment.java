package com.neighborhood.payment.entity;

import jakarta.persistence.*;
import lombok.Data;
import java.math.BigDecimal;
import java.time.LocalDateTime;

@Data
@Entity
@Table(name = "payments")
public class Payment {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(name = "order_id", unique = true, nullable = false)
    private String orderId;

    @Column(name = "trade_order_id")
    private String tradeOrderId;

    @Column(name = "user_id", nullable = false)
    private Long userId;

    @Column(name = "amount", nullable = false, precision = 10, scale = 2)
    private BigDecimal amount;

    @Column(name = "payment_method")
    private String paymentMethod; // wechat, alipay

    @Column(name = "status")
    private String status; // pending, paid, failed, refunded

    @Column(name = "transaction_id")
    private String transactionId;

    @Column(name = "payment_time")
    private LocalDateTime paymentTime;

    @Column(name = "notify_data", columnDefinition = "TEXT")
    private String notifyData;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
