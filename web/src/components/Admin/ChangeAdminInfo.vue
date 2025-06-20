<template>
  <div id="change-admin-info" class="section">
    <h1>修改管理员信息</h1>
    <a-form
      :model="formState"
      name="basic"
      :label-col="{ span: 2 }"
      :wrapper-col="{ span: 8 }"
      autocomplete="off"
      @finish="showPasswordModal"
      @finishFailed="onFinishFailed"
    >
      <a-form-item
        label="管理员昵称"
        name="adminname"
        :rules="[{ required: true, message: '请输入管理员昵称' }]"
      >
        <a-input v-model:value="formState.adminname" />
      </a-form-item>
      <a-form-item
        label="邮箱"
        name="email"
        :rules="[{ required: true, message: '请输入邮箱', type: 'email' }]"
      >
        <a-input v-model:value="formState.email" />
      </a-form-item>
      <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
        <a-button type="primary" html-type="submit">
          保存
        </a-button>
      </a-form-item>
    </a-form>

    <a-modal
      v-model:visible="isPasswordModalVisible"
      title="验证密码"
      @ok="handlePasswordOk"
      @cancel="handlePasswordCancel"
    >
      <a-form-item label="密码" :rules="[{ required: true, message: '请输入密码' }]">
        <a-input type="password" v-model:value="password" autocomplete="off" />
      </a-form-item>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import CryptoJS from 'crypto-js'
import { message } from 'ant-design-vue'

const formState = ref({
  adminname: '',
  email: ''
})
const password = ref('')
const isPasswordModalVisible = ref(false)

const fetchAdminInfo = async () => {
  try {
    const token = sessionStorage.getItem('adminToken')
    const response = await request.get('/api/admin/get', {
      headers: { 'x-access-token': token }
    })
    if (response.data.code === 200) {
      formState.value.adminname = response.data.data.adminname
      formState.value.email = response.data.data.email
    } else {
      message.error(response.data.message)
    }
  } catch (error) {
    message.error(error.response?.data?.message || '未知错误，请联系管理员')
  }
}

onMounted(fetchAdminInfo)

const showPasswordModal = () => {
  isPasswordModalVisible.value = true
}

const handlePasswordOk = async () => {
  try {
    const token = sessionStorage.getItem('adminToken')
    const encryptedPassword = CryptoJS.SHA256(password.value).toString()
    const response = await request.post(
      '/api/admin/set',
      {
        adminname: formState.value.adminname,
        email: formState.value.email,
        password: encryptedPassword
      },
      {
        headers: { 'x-access-token': token }
      }
    )
    if (response.data.code === 200) {
      isPasswordModalVisible.value = false
      password.value = ''
      message.success(response.data.message)
    } else {
      message.error(response.data.message)
    }
  } catch (error) {
    message.error(error.response?.data?.message || '未知错误，请联系管理员')
  }
}

const handlePasswordCancel = () => {
  isPasswordModalVisible.value = false
  password.value = ''
}

const onFinishFailed = (errorInfo) => {
  console.log('Failed:', errorInfo)
}
</script>

<style scoped>
.section {
  margin-top: 20px;
}
</style>