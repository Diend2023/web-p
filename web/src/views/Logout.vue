<template>
  <div style="background-image: url(../assets/index/1.png);">
    <div>正在退出登录...</div>
  </div>
</template>

<script>
import request from '@/utils/request'
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue'

export default {
  name: 'Logout',
  setup() {
    const router = useRouter();

    const logout = async () => {
      const token = sessionStorage.getItem('token');
      if (!token) {
        router.push('/');
        return;
      }

      try {
        const response = await request.post('/api/user/logout', {}, {
          headers: {
            'x-access-token': token
          }
        });
        if (response.data.code === 200 || response.data.code === 201) {
          message.success(response.data.message);
        } else {
          message.error(response.data.message);
        }
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('dashboardSelectedKeys');
        router.push('/');
      } catch (error) {
        message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
        sessionStorage.removeItem('token');
        sessionStorage.removeItem('dashboardSelectedKeys');
        router.push('/');
      }
    };

    onMounted(() => {
      logout();
    });
  }
};
</script>