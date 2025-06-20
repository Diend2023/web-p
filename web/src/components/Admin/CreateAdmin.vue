<template>
  <a-modal
    v-model:visible="isVisible"
    title="创建管理员"
    @ok="handleOk"
    @cancel="handleCancel"
    ok-text="创建"
    cancel-text="取消"
  >
    <a-form :model="formState" :label-col="{ span: 6 }" :wrapper-col="{ span: 28 }">
      <a-form-item
        label="管理员昵称"
        prop="adminname"
        :rules="[{ required: true, message: '请输入管理员昵称' }]"
      >
        <a-input v-model:value="formState.adminname" placeholder="输入管理员昵称" />
      </a-form-item>
      <a-form-item
        label="邮箱"
        prop="email"
        :rules="[{ required: true, type: 'email', message: '请输入有效邮箱' }]"
      >
        <a-input v-model:value="formState.email" placeholder="输入邮箱" />
      </a-form-item>
      <a-form-item
        label="密码"
        prop="password"
        :rules="[{ required: true, message: '请输入密码' }]"
      >
        <a-input-password v-model:value="formState.password" placeholder="输入密码" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { ref, reactive, defineEmits } from 'vue'
import request from '@/utils/request'
import { message } from 'ant-design-vue'
import CryptoJS from 'crypto-js'

const emit = defineEmits(['created'])

// 控制模态框显示
const isVisible = ref(false)

// 表单数据
const formState = reactive({
  adminname: '',
  email: '',
  password: ''
})

// 管理员 token
const token = sessionStorage.getItem('adminToken')

// 提交创建请求
const handleOk = async () => {
  if (!formState.adminname || !formState.email || !formState.password) {
    return message.error('请输入完整信息')
  }
  const encryptedPassword = CryptoJS.SHA256(formState.password).toString()
  formState.password = encryptedPassword
  try {
    const res = await request.post('/api/admin/admin/create', formState, {
      headers: { 'x-access-token': token }
    })
    if (res.data.code === 200) {
      message.success('创建管理员成功')
      // 可根据需要重置表单或关闭对话框
      isVisible.value = false
      // 重置表单
      formState.adminname = ''
      formState.email = ''
      formState.password = ''
      emit('created')
    } else {
      message.error(res.data.message)
    }
  } catch (err) {
    message.error(err.response?.data?.message || '创建管理员失败')
  }
}

const handleCancel = () => {
  isVisible.value = false
}
  
// 暴露控制方法
defineExpose({ isVisible })
</script>