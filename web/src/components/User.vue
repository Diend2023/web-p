<template>
  <div class="context_box">
    <a-menu mode="horizontal" :selected-keys="[currentSection]" @click="handleMenuClick">
      <a-menu-item key="user-info">用户信息</a-menu-item>
      <a-menu-item key="change-info">修改信息</a-menu-item>
      <a-menu-item key="change-password">修改密码</a-menu-item>
      <a-menu-item key="account">账户设置</a-menu-item>
    </a-menu>
    <component :is="currentComponent" :userInfo="userInfo" @updateUserInfo="updateUserInfo" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import UserInfo from '@/components/User/UserInfo.vue';
import ChangeInfo from '@/components/User/ChangeInfo.vue';
import ChangePassword from '@/components/User/ChangePassword.vue';
import Account from '@/components/User/Account.vue';

const currentSection = ref('user-info');
const userInfo = ref(null);

const componentsMap = {
  'user-info': UserInfo,
  'change-info': ChangeInfo,
  'change-password': ChangePassword,
  'account': Account
};

const currentComponent = computed(() => componentsMap[currentSection.value]);

const updateUserInfo = (updatedInfo) => {
  userInfo.value = updatedInfo;
};

const handleMenuClick = (e) => {
  currentSection.value = e.key;
};
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

}
</style>