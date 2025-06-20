<template>

  <div class="bg">
    <div class="container right-panel-active">
      <div class="w" style="width: 800px;"></div>
      <!-- Sign Up -->
      <div class="container__form container--signup">
        <form @submit.prevent="register" class="form" id="form1">
          <h2 class="form__title">注册</h2>
          <input type="text" v-model="username" placeholder="用户名" class="input" required />
          <input type="email" v-model="email" placeholder="邮箱" class="input" required />
          <input type="password" v-model="password" placeholder="密码" class="input" required />
          <button class="btn" type="submit">提交</button>
        </form>
      </div>

      <!-- Sign In -->
      <div class="container__form container--signin">
        <form @submit.prevent="login" class="form" id="form2">
          <h2 class="form__title">登录</h2>
          <input type="email" v-model="email" placeholder="邮箱" class="input" required />
          <input type="password" v-model="password" placeholder="密码" class="input" required />
          <button class="btn" type="submit">提交</button>
        </form>
      </div>

      <!-- Overlay -->
      <div class="container__overlay">
        <div class="overlay">
          <div class="overlay__panel overlay--left">
            <button class="btn" id="signIn">转到登录</button>
          </div>
          <div class="overlay__panel overlay--right">
            <button class="btn" id="signUp">转到注册</button>
          </div>
        </div>
      </div>
    </div>

    <!-- <div>
    <h1>Register</h1>
    <form @submit.prevent="register">
      <input type="text" v-model="username" placeholder="Username" required />
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit">Register</button>
    </form>
  </div> -->

    <!-- <div>
    <h1>Login</h1>
    <form @submit.prevent="login">
      <input type="email" v-model="email" placeholder="Email" required />
      <input type="password" v-model="password" placeholder="Password" required />
      <button type="submit">Login</button>
    </form>
  </div> -->
  </div>
</template>

<script>
import request from '@/utils/request'
import '@/assets/login/login.css';
import * as js from '@/assets/login/login.js';
import { message } from 'ant-design-vue'
import CryptoJS from 'crypto-js';

export default {
  name: 'RegisterOrlogin',
  data() {
    return {
      username: '',
      email: '',
      password: ''
    };
  },
  mounted() {
    js.changeForm();
  },
  methods: {
    async register() {
      const encryptedPassword = CryptoJS.SHA256(this.password).toString();
      await this.handleRequest('/api/user/register', {
        username: this.username,
        email: this.email,
        password: encryptedPassword
      }, () => {
        document.getElementById('signIn').click();
      });
    },
    async login() {
      const encryptedPassword = CryptoJS.SHA256(this.password).toString();
      await this.handleRequest('/api/user/login', {
        email: this.email,
        password: encryptedPassword
      }, (response) => {
        const token = response.data.data && response.data.data.token;
        if (token) {
          sessionStorage.setItem('token', token);
          this.$router.push('/');
        }
      });
    },
    async handleRequest(url, data, onSuccess) {
      try {
        const response = await request.post(url, data);
        if (response.data.code === 200 || response.data.code === 201) {
          message.success(response.data.message);
        } else {
          message.error(response.data.message);
        }
        if (onSuccess) onSuccess(response);
      } catch (error) {
        this.handleError(error);
      }
    },
    handleError(error) {
      if (!error.response || !error.response.data.message) {
        message.error('未知错误，请联系管理员');
      } else {
        message.error(error.response.data.message);
      }
    }
  }
}
</script>
