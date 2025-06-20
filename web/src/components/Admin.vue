<template>
  <div class="context_box">
    <a-menu
      mode="horizontal"
      :selected-keys="[currentSection]"
      @click="handleMenuClick"
    >
      <a-menu-item key="admin-info">管理员信息</a-menu-item>
      <a-menu-item key="change-info">修改信息</a-menu-item>
      <a-menu-item key="change-password">修改密码</a-menu-item>
      <a-menu-item key="admin-account">账户设置</a-menu-item>
    </a-menu>
    <component
      :is="currentComponent"
      :adminInfo="adminInfo"
      @updateAdminInfo="updateAdminInfo"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import AdminInfo from '@/components/Admin/AdminInfo.vue'
import ChangeAdminInfo from '@/components/Admin/ChangeAdminInfo.vue'
import ChangeAdminPassword from '@/components/Admin/ChangeAdminPassword.vue'
import AdminAccount from '@/components/Admin/AdminAccount.vue'

const currentSection = ref('admin-info')
const adminInfo = ref(null)

const componentsMap = {
  'admin-info': AdminInfo,
  'change-info': ChangeAdminInfo,
  'change-password': ChangeAdminPassword,
  'admin-account': AdminAccount
}

const currentComponent = computed(() => componentsMap[currentSection.value])

const updateAdminInfo = (updatedInfo) => {
  adminInfo.value = updatedInfo
}

const handleMenuClick = (e) => {
  currentSection.value = e.key
}
</script>

<style scoped>
.context_box {
  height: 100vh;
  width: 100%;
}

.section {
  margin-top: 20px;
}

@media screen and (max-width: 1080px) {
  /* 自定义响应式样式 */
}
</style>