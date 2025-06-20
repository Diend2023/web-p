<template>
  <div class="admin-login">
    <a-card title="管理员登录" class="login-card">
      <a-form
        :model="formState"
        name="adminLogin"
        :label-col="{ span: 4 }"
        :wrapper-col="{ span: 16 }"
        autocomplete="off"
        @finish="onFinish"
        @finishFailed="onFinishFailed"
      >
        <a-form-item
          label="邮箱"
          name="email"
          :rules="[
            { required: true, message: '请输入邮箱!' },
            { type: 'email', message: '邮箱格式不正确!' }
          ]"
        >
          <a-input v-model:value="formState.email" />
        </a-form-item>
        <a-form-item
          label="密码"
          name="password"
          :rules="[{ required: true, message: '请输入密码!' }]"
        >
          <a-input-password v-model:value="formState.password" />
        </a-form-item>
        <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
          <a-button type="primary" html-type="submit">登录</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request'
import CryptoJS from 'crypto-js';
import { message } from 'ant-design-vue';

const router = useRouter();
const formState = reactive({
  email: '',
  password: ''
});

const onFinish = async () => {
  const encryptedPassword = CryptoJS.SHA256(formState.password).toString();
  try {
    const response = await request.post('/api/admin/login', {
      email: formState.email,
      password: encryptedPassword
    });
    const adminToken = response.data.data && response.data.data.admin_token;
    if (adminToken) {
      sessionStorage.setItem('adminToken', adminToken);
      message.success('登录成功');
      router.push('/admin/dashboard');
    } else {
      message.error('登录失败：邮箱或密码错误');
    }
  } catch (error) {
    message.error(error.response?.data?.message || '未知错误，请联系管理员');
  }
};

const onFinishFailed = (errorInfo) => {
  console.log('Failed:', errorInfo);
};
</script>

<style scoped>
.admin-login {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.login-card {
  width: 400px;
}
</style>