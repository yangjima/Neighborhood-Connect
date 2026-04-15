package com.neighborhood.user.service;

import com.neighborhood.user.entity.User;
import org.springframework.stereotype.Service;

@Service
public interface UserService {
    User findByPhone(String phone);
    User findById(Long id);
    User save(User user);
}
