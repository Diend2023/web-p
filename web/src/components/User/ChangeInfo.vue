<template>
  <div id="change-info" class="section">
    <h1>修改信息</h1>
    <a-form :model="formState" name="basic" :label-col="{ span: 2 }" :wrapper-col="{ span: 8 }" autocomplete="off"
      @finish="showPasswordModal" @finishFailed="onFinishFailed">
      <a-form-item label="用户名" name="username" :rules="[{ required: true, message: '请输入用户名' }]">
        <a-input v-model:value="formState.username" />
      </a-form-item>
      <a-form-item label="邮箱" name="email" :rules="[{ required: true, message: '请输入邮箱', type: 'email' }]">
        <a-input v-model:value="formState.email" />
      </a-form-item>
      <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
        <a-button type="primary" html-type="submit">
          保存
        </a-button>
      </a-form-item>
    </a-form>

    <a-modal v-model:visible="isPasswordModalVisible" title="验证密码" @ok="handlePasswordOk"
      @cancel="handlePasswordCancel">
      <a-form-item label="密码" :rules="[{ required: true, message: '请输入密码' }]">
        <a-input type="password" v-model:value="password" autocomplete="off" />
      </a-form-item>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '@/utils/request'
import CryptoJS from 'crypto-js';
import { message } from 'ant-design-vue';


const formState = ref({
  username: '',
  email: ''
});
const password = ref('');
const isPasswordModalVisible = ref(false);

const fetchUserInfo = async () => {
  try {
    const token = sessionStorage.getItem('token');
    const response = await request.get('/api/user/get', {
      headers: {
        'x-access-token': token
      }
    });

    if (response.data.code === 200 || response.data.code === 201) {
      formState.value.username = response.data.data.username;
      formState.value.email = response.data.data.email;
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
  }
};

onMounted(() => {
  fetchUserInfo();
});

const showPasswordModal = () => {
  isPasswordModalVisible.value = true;
};

const handlePasswordOk = async () => {
  try {
    const token = sessionStorage.getItem('token');
    const encryptedPassword = CryptoJS.SHA256(password.value).toString();
    const response = await request.post('/api/user/set', { ...formState.value, password: encryptedPassword }, {
      headers: {
        'x-access-token': token
      }
    });
    if (response.data.code === 200 || response.data.code === 201) {
      isPasswordModalVisible.value = false;
      password.value = '';
      message.success(response.data.message);
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
  }
};

const handlePasswordCancel = () => {
  isPasswordModalVisible.value = false;
  password.value = '';
};

const onFinishFailed = (errorInfo) => {
  console.log('Failed:', errorInfo);
};
</script>

<style scoped>
.section {
  margin-top: 20px;
}
</style>