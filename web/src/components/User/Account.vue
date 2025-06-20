<template>
  <div id="account" class="section">
    <h1>账户设置</h1>
    <a-button type="primary" @click="logout">退出登录</a-button>
    <a-button type="primary" @click="showDeleteAccountModal" danger>注销账户</a-button>

    <a-modal v-model:visible="isDeleteAccountModalVisible" title="验证密码" @ok="handleDeleteAccountOk"
      @cancel="handleDeleteAccountCancel">
      <a-form>
        <a-form-item label="验证密码" :rules="[{ required: true, message: '请输入密码' }]">
          <a-input type="password" v-model:value="password" />
        </a-form-item>
        <a-form-item label="确认注销" :rules="[{ required: true, message: '请输入“确认注销账户”加上您的昵称' }]"
          help="请输入“确认注销账户”加上您的昵称">
          <a-input v-model:value="deleteAccountVerification" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request'
import CryptoJS from 'crypto-js';
import { message } from 'ant-design-vue';

const router = useRouter();
const isDeleteAccountModalVisible = ref(false);
const password = ref('');
const deleteAccountVerification = ref('');
const user_name = ref('');

const fetchUserInfo = async () => {
  try {
    const token = sessionStorage.getItem('token');
    const response = await request.get('/api/user/get', {
      headers: {
        'x-access-token': token
      }
    });
    if (response.data.code === 200 || response.data.code === 201) {
      user_name.value = response.data.data.username;
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

const logout = () => {
  router.push('/logout');
};

const showDeleteAccountModal = () => {
  isDeleteAccountModalVisible.value = true;
};

const handleDeleteAccountOk = async () => {
  if (deleteAccountVerification.value !== `确认注销账户${user_name.value}`) {
    message.error('确认信息不正确，请输入“确认注销账户”加上您的昵称');
    return;
  }

  try {
    const token = sessionStorage.getItem('token');
    const encryptedPassword = CryptoJS.SHA256(password.value).toString();
    const response = await request.post('/api/user/del', { password: encryptedPassword }, {
      headers: {
        'x-access-token': token
      }
    });
    if (response.data.code === 200 || response.data.code === 201) {
      message.success(response.data.message);
      isDeleteAccountModalVisible.value = false;
      password.value = '';
      deleteAccountVerification.value = '';
      sessionStorage.removeItem('token');
      router.push('/');
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
  }
};

const handleDeleteAccountCancel = () => {
  isDeleteAccountModalVisible.value = false;
  password.value = '';
  deleteAccountVerification.value = '';
};
</script>

<style scoped>
.section {
  margin-top: 20px;
}

button {
  margin-right: 20px;
  margin-top: 20px;
}
</style>