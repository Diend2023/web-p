<template>
  <div id="user-info" class="section">
    <h1>用户信息</h1>
    <div v-if="loading">加载中...</div>
    <div v-else-if="error">{{ error }}</div>
    <div v-else>
      <p><strong>UID：</strong> {{ userInfo.user_id }}</p>
      <p><strong>用户名：</strong> {{ userInfo.username }}</p>
      <p><strong>邮箱：</strong> {{ userInfo.email }}</p>
      <p><strong>注册时间：</strong> {{ userInfo.create_time }}</p>
      <p><strong>最后修改时间：</strong> {{ userInfo.update_time }}</p>
      <p><strong>最后登录时间：</strong> {{ userInfo.last_login_time }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '@/utils/request'
import { message } from 'ant-design-vue';

const userInfo = ref(null);
const loading = ref(true);
const error = ref(null);

const fetchUserInfo = async () => {
  try {
    const token = sessionStorage.getItem('token');
    const response = await request.get('/api/user/get', {
      headers: {
        'x-access-token': token
      }
    });
    if (response.data.code === 200 || response.data.code === 201) {
      userInfo.value = response.data.data;
      message.success(response.data.message);
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
  } finally {
    loading.value = false;
  }
};

onMounted(fetchUserInfo);
</script>

<style scoped>
.section {
  margin-top: 20px;
}
</style>