import axios from 'axios'
import config from '@/config'

// 创建 axios 实例
const request = axios.create({
  baseURL: config.API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

export default request