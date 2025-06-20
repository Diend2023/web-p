<template>
  <div id="admin-info" class="section">
    <h1>管理员信息</h1>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <p><strong>管理员ID：</strong> {{ adminInfo.a_id }}</p>
      <p><strong>管理员AID：</strong> {{ adminInfo.admin_id }}</p>
      <p><strong>管理员昵称：</strong> {{ adminInfo.adminname }}</p>
      <p><strong>邮箱：</strong> {{ adminInfo.email }}</p>
      <p><strong>注册时间：</strong> {{ adminInfo.create_time }}</p>
      <p><strong>最后修改时间：</strong> {{ adminInfo.update_time }}</p>
      <p v-if="adminInfo.last_login_time">
        <strong>最后登录时间：</strong> {{ adminInfo.last_login_time }}
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { message } from 'ant-design-vue'

const adminInfo = ref(null)
const loading = ref(true)
const error = ref(null)

const fetchAdminInfo = async () => {
  try {
    const token = sessionStorage.getItem('adminToken')
    const response = await request.get('/api/admin/get', {
      headers: { 'x-access-token': token }
    })
    if (response.data.code === 200) {
      adminInfo.value = response.data.data
      message.success(response.data.message)
    } else {
      error.value = response.data.message
      message.error(response.data.message)
    }
  } catch (err) {
    error.value = err.response?.data?.message || '未知错误，请联系管理员'
    message.error(error.value)
  } finally {
    loading.value = false
  }
}

onMounted(fetchAdminInfo)
</script>

<style scoped>
.section {
  margin-top: 20px;
}
</style>