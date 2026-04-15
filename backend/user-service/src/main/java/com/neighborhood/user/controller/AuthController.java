package com.neighborhood.user.controller;

import com.neighborhood.user.dto.*;
import com.neighborhood.user.entity.User;
import com.neighborhood.user.security.JwtTokenProvider;
import com.neighborhood.user.service.UserService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.http.ResponseEntity;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.web.bind.annotation.*;

import java.time.Duration;
import java.util.HashMap;
import java.util.Map;

@RestController
@RequestMapping("/api/user")
public class AuthController {

    @Autowired
    private UserService userService;

    @Autowired
    private JwtTokenProvider tokenProvider;

    @Autowired
    private PasswordEncoder passwordEncoder;

    @Autowired
    private StringRedisTemplate redisTemplate;

    @PostMapping("/login")
    public ResponseEntity<?> login(@Valid @RequestBody LoginRequest request) {
        User user = userService.findByPhone(request.getPhone());

        if (user == null || !passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            return ResponseEntity.badRequest().body(Map.of("message", "手机号或密码错误"));
        }

        String token = tokenProvider.generateToken(user.getId(), user.getUserType());

        AuthResponse response = new AuthResponse(
                token,
                "Bearer",
                user.getId(),
                user.getNickname(),
                user.getUserType()
        );

        return ResponseEntity.ok(response);
    }

    @PostMapping("/register")
    public ResponseEntity<?> register(@Valid @RequestBody RegisterRequest request) {
        // 验证验证码
        String cachedCode = redisTemplate.opsForValue().get("sms:code:" + request.getPhone());
        if (cachedCode == null || !cachedCode.equals(request.getCode())) {
            return ResponseEntity.badRequest().body(Map.of("message", "验证码错误或已过期"));
        }

        // 检查用户是否已存在
        if (userService.findByPhone(request.getPhone()) != null) {
            return ResponseEntity.badRequest().body(Map.of("message", "该手机号已注册"));
        }

        // 创建新用户
        User user = new User();
        user.setPhone(request.getPhone());
        user.setPassword(passwordEncoder.encode(request.getPassword()));
        user.setUserType(request.getUserType());
        user.setNickname("用户" + request.getPhone().substring(request.getPhone().length() - 4));
        user.setStatus("active");

        user = userService.save(user);

        // 删除验证码
        redisTemplate.delete("sms:code:" + request.getPhone());

        Map<String, Object> result = new HashMap<>();
        result.put("message", "注册成功");
        result.put("userId", user.getId());

        return ResponseEntity.ok(result);
    }

    @PostMapping("/send-code")
    public ResponseEntity<?> sendCode(@RequestBody SendCodeRequest request) {
        // 生成6位验证码
        String code = String.format("%06d", (int) (Math.random() * 1000000));

        // 存入Redis（5分钟有效）
        redisTemplate.opsForValue().set("sms:code:" + request.getPhone(), code, Duration.ofMinutes(5));

        // TODO: 调用短信服务商发送验证码
        // 这里模拟发送成功
        System.out.println("验证码已发送至 " + request.getPhone() + "，验证码: " + code);

        return ResponseEntity.ok(Map.of("message", "验证码已发送"));
    }

    @GetMapping("/profile")
    public ResponseEntity<?> getProfile(@RequestHeader("Authorization") String authHeader) {
        try {
            String token = authHeader.replace("Bearer ", "");
            Long userId = tokenProvider.getUserIdFromToken(token);
            User user = userService.findById(userId);

            if (user == null) {
                return ResponseEntity.notFound().build();
            }

            // 不返回密码
            user.setPassword(null);
            return ResponseEntity.ok(user);
        } catch (Exception e) {
            return ResponseEntity.status(401).body(Map.of("message", "未授权"));
        }
    }

    @PostMapping("/logout")
    public ResponseEntity<?> logout() {
        return ResponseEntity.ok(Map.of("message", "退出成功"));
    }
}
