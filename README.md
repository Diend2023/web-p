# WEB-P

该项目是一个本人学习开发的前后端分离的Flask + Vue项目，可以为用户提供静态网页托管功能。

### demo

https://webp.wanqifan.top

# server

server文件夹的内容为该项目的后端项目，你需要：[Python](https://www.python.org/)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置
将.env.example文件复制为.env，填入你的配置，然后运行

```bash
python run.py
```

# web

web文件夹的内容为该项目的前端项目，你需要：[Node.js](https://nodejs.cn/)

### 安装依赖

```bash
npm install
```

### 开发

确认vite.config.js和vue.config.js中的代理地址，然后运行
```bash
npm run dev
```

### 构建

确认web/src/config.js中production的API_BASE_URL为部署的后端地址，然后运行
```bash
npm run build
```
