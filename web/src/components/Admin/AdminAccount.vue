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
const adminname = ref('');

const fetchAdminInfo = async () => {
  try {
    const token = sessionStorage.getItem('adminToken');
    const response = await request.get('/api/admin/get', {
      headers: { 'x-access-token': token }
    });
    if (response.data.code === 200) {
      adminname.value = response.data.data.adminname;
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '未知错误，请联系管理员');
  }
};

onMounted(() => {
  fetchAdminInfo();
});

const logout = () => {
  router.push('/admin/logout');
};

const showDeleteAccountModal = () => {
  isDeleteAccountModalVisible.value = true;
};

const handleDeleteAccountOk = async () => {
  // 校验注销确认信息
  if (deleteAccountVerification.value !== `确认注销账户${adminname.value}`) {
    message.error('确认信息不正确，请输入“确认注销账户”加上您的昵称');
    return;
  }
  
  try {
    const token = sessionStorage.getItem('adminToken');
    const encryptedPassword = CryptoJS.SHA256(password.value).toString();
    const response = await request.post('/api/admin/del', { password: encryptedPassword }, {
      headers: { 'x-access-token': token }
    });
    if (response.data.code === 200) {
      message.success(response.data.message);
      isDeleteAccountModalVisible.value = false;
      password.value = '';
      deleteAccountVerification.value = '';
      sessionStorage.removeItem('adminToken');
      sessionStorage.removeItem('dashboardSelectedKeys');
      router.push('/admin/login');
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '未知错误，请联系管理员');
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