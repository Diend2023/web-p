<template>
  <div id="change-admin-password" class="section">
    <h1>修改管理员密码</h1>
    <a-form
      :model="formState"
      name="changeAdminPassword"
      :label-col="{ span: 2 }"
      :wrapper-col="{ span: 8 }"
      autocomplete="off"
      @finish="changePassword"
      @finishFailed="onFinishFailed"
    >
      <a-form-item
        label="旧密码"
        name="oldPassword"
        :rules="[{ required: true, message: '请输入旧密码' }]"
      >
        <a-input type="password" v-model:value="formState.oldPassword" />
      </a-form-item>
      <a-form-item
        label="新密码"
        name="newPassword"
        :rules="[{ required: true, message: '请输入新密码' }]"
      >
        <a-input type="password" v-model:value="formState.newPassword" />
      </a-form-item>
      <a-form-item
        label="重复新密码"
        name="confirmNewPassword"
        :rules="[
          { required: true, message: '请重复输入新密码' },
          { validator: validateConfirmPassword }
        ]"
      >
        <a-input type="password" v-model:value="formState.confirmNewPassword" />
      </a-form-item>
      <a-form-item :wrapper-col="{ offset: 8, span: 16 }">
        <a-button type="primary" html-type="submit">
          修改密码
        </a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import request from '@/utils/request'
import CryptoJS from 'crypto-js'
import { message } from 'ant-design-vue'

const formState = ref({
  oldPassword: '',
  newPassword: '',
  confirmNewPassword: ''
})

const validateConfirmPassword = (rule, value) => {
  if (value !== formState.value.newPassword) {
    return Promise.reject('两次输入的新密码不一致')
  }
  return Promise.resolve()
}

const changePassword = async () => {
  try {
    const token = sessionStorage.getItem('adminToken')
    const encryptedOldPassword = CryptoJS.SHA256(formState.value.oldPassword).toString()
    const encryptedNewPassword = CryptoJS.SHA256(formState.value.newPassword).toString()
    const response = await request.post(
      '/api/admin/password',
      {
        oldPassword: encryptedOldPassword,
        newPassword: encryptedNewPassword
      },
      {
        headers: { 'x-access-token': token }
      }
    )
    if (response.data.code === 200) {
      message.success(response.data.message)
      formState.value.oldPassword = ''
      formState.value.newPassword = ''
      formState.value.confirmNewPassword = ''
    } else {
      message.error(response.data.message)
    }
  } catch (error) {
    message.error(error.response?.data?.message || '未知错误，请联系管理员')
  }
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