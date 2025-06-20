<template>
  <div style="text-align: center; margin-top: 50px;">
    正在进入管理员后台，请稍候...
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request'
import { message } from 'ant-design-vue';

const router = useRouter();

onMounted(async () => {
  const adminToken = sessionStorage.getItem('adminToken');
  if (!adminToken || adminToken === 'undefined') {
    // 没有token时直接跳转到登录页
    router.push('/admin/login');
    return;
  }
  try {
    const response = await request.post('/api/admin/verify', {}, {
      headers: {
        'x-access-token': adminToken
      }
    });
    if (response.data.code === 200 || response.data.code === 201) {
      router.push('/admin/dashboard');
    } else {
      sessionStorage.removeItem('adminToken');
      message.error(response.data.message || '管理员验证失败');
      router.push('/admin/login');
    }
  } catch (error) {
    sessionStorage.removeItem('adminToken');
    message.error(error.response?.data?.message || '管理员验证失败');
    router.push('/admin/login');
  }
});
</script>