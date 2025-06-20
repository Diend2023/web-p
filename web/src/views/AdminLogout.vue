<template>
  <div style="background-image: url(../assets/index/1.png);">
    <div>正在退出登录...</div>
  </div>
</template>

<script>
import request from '@/utils/request'
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { message } from 'ant-design-vue';

export default {
  name: 'AdminLogout',
  setup() {
    const router = useRouter();

    const logout = async () => {
      const token = sessionStorage.getItem('adminToken');
      if (!token) {
        router.push('/admin/login');
        return;
      }

      try {
        const response = await request.post('/api/admin/logout', {}, {
          headers: {
            'x-access-token': token
          }
        });
        if (response.data.code === 200) {
          message.success(response.data.message);
        } else {
          message.error(response.data.message);
        }
        sessionStorage.removeItem('adminToken');
        sessionStorage.removeItem('dashboardSelectedKeys');
        router.push('/admin/login');
      } catch (error) {
        message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
        sessionStorage.removeItem('adminToken');
        sessionStorage.removeItem('dashboardSelectedKeys');
        router.push('/admin/login');
      }
    };

    onMounted(() => {
      logout();
    });

    return {};
  }
};
</script>