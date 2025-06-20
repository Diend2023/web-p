/*
 Navicat Premium Dump SQL

 Source Server         : localhost_mysql
 Source Server Type    : MySQL
 Source Server Version : 50744 (5.7.44-log)
 Source Host           : localhost:3306
 Source Schema         : web_p

 Target Server Type    : MySQL
 Target Server Version : 50744 (5.7.44-log)
 File Encoding         : 65001

 Date: 08/05/2025 23:25:16
*/

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for admins
-- ----------------------------
DROP TABLE IF EXISTS `admins`;
CREATE TABLE `admins`  (
  `a_id` int(11) NOT NULL AUTO_INCREMENT,
  `admin_id` varchar(36) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `adminname` varchar(24) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `email` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `last_login_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`a_id`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 4 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of admins
-- ----------------------------
INSERT INTO `admins` VALUES (1, '603fd1f2-cd3b-433c-aa47-88d4e16f5d6e', '123', '123@123.com', '$2b$12$nnhXN.VhMbSPt8J6ez9z4uMVbrHpIgRO3tVox2eKVQQWxmYwSYuJK', '2025-04-07 19:45:33', '2025-05-07 01:29:25', '2025-05-08 22:50:12');
INSERT INTO `admins` VALUES (3, 'c5b971af-7fac-4f1d-9741-849044c26421', '456', '456@456.com', '$2b$12$vHsbje1lhKG1OeSa6Qr1G.g80GttBZ2OzwQaaKw0iX21cLqSTdqkG', '2025-05-06 23:42:04', '2025-05-06 23:42:04', '2025-05-06 23:42:26');

-- ----------------------------
-- Table structure for templates
-- ----------------------------
DROP TABLE IF EXISTS `templates`;
CREATE TABLE `templates`  (
  `t_id` int(11) NOT NULL AUTO_INCREMENT,
  `t_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `t_description` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `t_author` int(11) NULL DEFAULT NULL,
  `create_time` datetime NULL DEFAULT NULL,
  `update_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`t_id`) USING BTREE,
  INDEX `t_author-a_id`(`t_author`) USING BTREE,
  CONSTRAINT `t_author-a_id` FOREIGN KEY (`t_author`) REFERENCES `admins` (`a_id`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 24 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of templates
-- ----------------------------
INSERT INTO `templates` VALUES (1, 'Hello World 你好 世界', 'Hello World', 1, '2025-05-02 23:49:31', '2025-05-02 23:49:34');
INSERT INTO `templates` VALUES (2, '飞机大战', '一个简单的小游戏', 1, '2025-05-02 23:49:37', '2025-05-02 23:49:39');
INSERT INTO `templates` VALUES (3, 'Music Player', '一个简单的本地音乐播放器', 1, '2025-05-03 00:30:05', '2025-05-08 22:57:29');
INSERT INTO `templates` VALUES (23, 'test14', 'test14', 1, '2025-05-06 14:09:22', '2025-05-08 22:51:31');

-- ----------------------------
-- Table structure for users
-- ----------------------------
DROP TABLE IF EXISTS `users`;
CREATE TABLE `users`  (
  `u_id` int(11) UNSIGNED ZEROFILL NOT NULL AUTO_INCREMENT,
  `user_id` varchar(36) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `username` varchar(24) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `email` varchar(50) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `password` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `create_time` datetime NOT NULL,
  `update_time` datetime NOT NULL,
  `last_login_time` datetime NULL DEFAULT NULL,
  PRIMARY KEY (`u_id`) USING BTREE,
  UNIQUE INDEX `unique_email`(`email`) USING BTREE
) ENGINE = InnoDB AUTO_INCREMENT = 2 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of users
-- ----------------------------
INSERT INTO `users` VALUES (00000000001, 'f43314e8-b17c-498c-8c7e-697180c38522', '123', '123@123.com', '$2b$12$dlCDmKy7u0bo.X1OXf4RWefTSIQKfQ0YlHoe6sXAlKZwhlxrQHjAm', '2024-12-07 20:34:12', '2025-05-06 15:47:43', '2025-05-08 22:01:40');

-- ----------------------------
-- Table structure for works
-- ----------------------------
DROP TABLE IF EXISTS `works`;
CREATE TABLE `works`  (
  `w_id` int(11) NOT NULL AUTO_INCREMENT,
  `u_id` int(11) UNSIGNED NOT NULL,
  `t_id` int(11) NULL DEFAULT NULL,
  `w_name` varchar(100) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `w_description` text CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL,
  `visit_count` int(11) UNSIGNED ZEROFILL NOT NULL DEFAULT 00000000000,
  `create_time` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  `update_time` datetime NOT NULL,
  PRIMARY KEY (`w_id`) USING BTREE,
  INDEX `t_id-t_id`(`t_id`) USING BTREE,
  INDEX `u_id-u_id`(`u_id`) USING BTREE,
  CONSTRAINT `t_id-t_id` FOREIGN KEY (`t_id`) REFERENCES `templates` (`t_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `u_id-u_id` FOREIGN KEY (`u_id`) REFERENCES `users` (`u_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB AUTO_INCREMENT = 45 CHARACTER SET = utf8 COLLATE = utf8_general_ci ROW_FORMAT = Dynamic;

-- ----------------------------
-- Records of works
-- ----------------------------
INSERT INTO `works` VALUES (38, 1, NULL, 'test9', 'test9', 00000000003, '2025-05-08 22:58:03', '2025-05-06 15:02:36');
INSERT INTO `works` VALUES (42, 1, 2, 'test10', 'test10', 00000000015, '2025-05-08 22:02:43', '2025-05-07 01:45:47');
INSERT INTO `works` VALUES (44, 1, 3, 'm', 'm', 00000000012, '2025-05-08 22:58:44', '2025-05-08 22:58:44');

SET FOREIGN_KEY_CHECKS = 1;
