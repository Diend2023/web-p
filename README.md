# WEB-P

一个基于 Flask + Vue 3 的前后端分离静态网页托管平台，支持在线代码编辑、模板管理和作品发布。

## ✨ 特性

- 🎨 **模板系统** - 提供网页模板，快速创建项目
- 💻 **在线编辑** - 内置代码编辑器，支持 HTML/CSS/JavaScript
- 🚀 **实时预览** - 即时预览代码效果
- 📁 **文件管理** - 支持多文件上传和管理
- 👥 **用户系统** - 完整的用户注册、登录、权限管理
- 📱 **响应式设计** - 适配各种设备屏幕
- 🔒 **安全可靠** - JWT 认证、SQL 注入防护

## 🌐 在线演示

[https://webp.wanqifan.top](https://webp.wanqifan.top)

## 📋 技术栈

### 后端

- **框架**: Flask
- **数据库**: MySQL
- **缓存**: Redis
- **认证**: JWT
- **文件处理**: 本地存储

### 前端

- **框架**: Vue 3 + Composition API
- **构建工具**: Vite
- **UI 组件**: Ant Design Vue
- **代码编辑器**: CodeMirror
- **路由**: Vue Router

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+
- Redis

### 后端部署

1. **进入后端目录**

   ```bash
   cd server
   ```

2. **安装依赖**

   ```bash
   pip install -r requirements.txt
   ```

3. **配置环境变量**

   ```bash
   cp .env.example .env
   ```

   编辑 `.env` 文件，配置数据库连接等信息：

   ```bash
   SECRET_KEY=your-secret-key-here
   MYSQL_HOST=localhost
   MYSQL_USER=your-mysql-username
   MYSQL_PASSWORD=your-mysql-password
   MYSQL_DB=web_p
   REDIS_URL=redis://localhost:6379/0
   ```

4. **初始化数据库**

   ```bash
   # 创建数据库
   mysql -u root -p
   CREATE DATABASE web_p CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   
   # 导入数据库结构
   mysql -u root -p web_p < web_p.sql
   ```

5. **启动后端服务**

   ```bash
   python run.py
   ```

   服务将运行在 `http://localhost:5000`

### 前端部署

1. **进入前端目录**

   ```bash
   cd web
   ```

2. **安装依赖**

   ```bash
   npm install
   ```

3. **配置开发环境**

   检查 `vite.config.js` 中的代理配置：

   ```javascript
    server: {
      proxy: {
        '/api': {
          target: 'http://127.0.0.1:5000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\//, '')
        }
      }
    }
   ```

4. **启动开发服务**

   ```bash
   npm run dev
   ```

   访问 `http://localhost:5173`

### 生产环境构建

1. **配置生产环境**

   编辑 `web/src/config.js`：

   ```javascript
    const config = {
      development: {
        API_BASE_URL: '',
      },
      production: {
        API_BASE_URL: 'http://127.0.0.1:5000',
      }
    }
   ```

2. **构建前端**

   ```bash
   cd web
   npm run build
   ```

3. **部署构建产物**

   将 `web/dist` 目录部署到静态文件服务器（如 Nginx）

## 🤝 贡献指南

1. Fork 本仓库
2. 创建你的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交你的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

## 🐛 问题反馈

如果你发现了 bug 或有功能建议，请在 [Issues](https://github.com/your-username/flask_web-p/issues) 中提出。

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源协议。

## 🙏 致谢

感谢以下开源项目的支持：

- [Flask](https://flask.palletsprojects.com/)
- [Vue.js](https://vuejs.org/)
- [Ant Design Vue](https://antdv.com/)
- [CodeMirror](https://codemirror.net/)

---

⭐ 如果这个项目对你有帮助，请给它一个 Star！
