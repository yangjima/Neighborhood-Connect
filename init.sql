-- 邻里通数据库初始化脚本

CREATE DATABASE IF NOT EXISTS neighborhood;
USE neighborhood;

-- 用户表
CREATE TABLE IF NOT EXISTS users (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    phone VARCHAR(20) UNIQUE NOT NULL COMMENT '手机号',
    password VARCHAR(255) NOT NULL COMMENT '密码(加密)',
    nickname VARCHAR(50) COMMENT '昵称',
    avatar VARCHAR(255) COMMENT '头像URL',
    user_type VARCHAR(20) DEFAULT 'resident' COMMENT '用户类型: resident-居民, property-物业, merchant-商家',
    status VARCHAR(20) DEFAULT 'active' COMMENT '状态: active-活跃, disabled-禁用',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_phone (phone),
    INDEX idx_user_type (user_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- 房源表 (MySQL版本，用于搜索索引)
CREATE TABLE IF NOT EXISTS rentals (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    type VARCHAR(20) NOT NULL COMMENT 'whole-整租, shared-合租, single-单间',
    price DECIMAL(10, 2) NOT NULL,
    area DECIMAL(10, 2),
    community VARCHAR(100),
    address VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    facilities TEXT,
    images TEXT,
    description TEXT,
    contact VARCHAR(50),
    publisher_id BIGINT,
    status VARCHAR(20) DEFAULT 'available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (publisher_id) REFERENCES users(id),
    INDEX idx_type (type),
    INDEX idx_price (price),
    INDEX idx_community (community),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='房源表';

-- 商品表
CREATE TABLE IF NOT EXISTS trade_items (
    id VARCHAR(50) PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(20) NOT NULL COMMENT 'furniture-家具, appliance-家电, other-其他',
    price DECIMAL(10, 2) NOT NULL,
    condition VARCHAR(20) NOT NULL COMMENT 'new-全新, like_new-九成新, good-八成新, fair-七成新',
    images TEXT,
    description TEXT,
    location VARCHAR(255),
    seller_id BIGINT,
    status VARCHAR(20) DEFAULT 'available',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (seller_id) REFERENCES users(id),
    INDEX idx_category (category),
    INDEX idx_price (price),
    INDEX idx_condition (condition),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品表';

-- 订单表
CREATE TABLE IF NOT EXISTS orders (
    id VARCHAR(50) PRIMARY KEY,
    item_id VARCHAR(50),
    item_type VARCHAR(20) NOT NULL COMMENT 'rental/trade',
    buyer_id BIGINT,
    seller_id BIGINT,
    price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending-待支付, paid-已支付, completed-已完成, cancelled-已取消',
    payment_method VARCHAR(20),
    payment_no VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (buyer_id) REFERENCES users(id),
    FOREIGN KEY (seller_id) REFERENCES users(id),
    INDEX idx_buyer (buyer_id),
    INDEX idx_seller (seller_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='订单表';

-- 收藏表
CREATE TABLE IF NOT EXISTS favorites (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    item_id VARCHAR(50) NOT NULL,
    item_type VARCHAR(20) NOT NULL COMMENT 'rental/trade',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    UNIQUE KEY uk_user_item (user_id, item_id, item_type),
    INDEX idx_user (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='收藏表';

-- 管理员表
CREATE TABLE IF NOT EXISTS admins (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'admin',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='管理员表';
