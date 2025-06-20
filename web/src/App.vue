<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <!-- 仅当路由meta.admin不为true时才显示 header -->
    <template v-if="!$route.meta.admin">
      <header v-if="!$route.meta.hideLayout">
        <a href="/" class="brand"><img src="./assets/global/logo.png" alt="logo" height="48px"></a>
        <div class="menu-btn"></div>
        <div class="navigation">
          <div class="navigation-items">
            <a href="/">主页</a>
            <a href="#">关于</a>
            <router-link to="/templates">浏览</router-link>
            <router-link v-if="!userLoggedIn" to="/registerorlogin" :key="`${loginKey}-1`">注册/登录</router-link>
            <router-link v-if="userLoggedIn" to="/dashboard" :key="`${loginKey}-2`">控制台</router-link>
            <router-link v-if="userLoggedIn" to="/logout" :key="`${loginKey}-3`">登出</router-link>
          </div>
        </div>
      </header>
    </template>
    <template v-else>
      <header v-if="!$route.meta.hideLayout">
        <a href="/" class="brand"><img src="./assets/global/logo.png" alt="logo" height="48px"></a>
        <div class="navigation">
          <div class="navigation-items">
            <a href="/">主页</a>
            <router-link v-if="adminLoggedIn" to="/admin/logout">登出</router-link>
          </div>
        </div>
      </header>
    </template>
    <div class="main">
      <a-config-provider :locale="zhCN">
        <router-view />
      </a-config-provider>
    </div>
    <chat v-if="!$route.meta.hideLayout"></chat>
  </div>
</template>

<script>
import * as header from '@/assets/global/header.js';
import '@/assets/global/header.css';
import AIchat from '@/components/AIchat.vue';
import zhCN from "ant-design-vue/es/locale/zh_CN";

export default {
  name: 'App',
  components: {
    'chat': AIchat,
  },
  data() {
    return {
      loginKey: 0,
      userLoggedIn: null,
      adminLoggedIn: null,
      zhCN
    };
  },
  mounted() {
    header.header();
  },
  methods: {
    forceRerender() {
      this.loginKey += 1;
    }
  },
  watch: {
    $route() {
      this.userLoggedIn = sessionStorage.getItem('token');
      this.adminLoggedIn = sessionStorage.getItem('adminToken');
      this.forceRerender();
    }
  }
}
</script>

<style scoped>
html,
body {
  height: 100%;
  margin: 0;
  padding: 0;
}
#app {
  height: 100vh;
  overflow: hidden;
}
.main {
  margin-top: 48px;
  height: calc(100vh + 1px);
  overflow: auto;
}
</style>