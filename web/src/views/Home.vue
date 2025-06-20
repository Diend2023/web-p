<template>
  <div>
    <section class="home">
      <img class="video-slide active" src="../assets/index/1.png" alt="1">
      <img class="video-slide" src="../assets/index/2.png" alt="1">

      <div class="content active">
        <h1>简单方式<br><span>创建你的个人空间</span></h1>
        <p>使用最简单的方式，创建你的个人空间，展示你的作品，分享你的经验，让更多人认识你。
        </p>
        <router-link to="/dashboard">立刻开始</router-link>
      </div>

      <div class="content">
        <h1>多种模板<br><span>快速完成网页制作</span></h1>
        <p>我们提供多种模板，让你快速完成网页制作，无需任何编程知识，只需简单的操作，即可完成你的网页。</p>
        <router-link to="/templates">浏览模板</router-link>
      </div>

      <div class="media-icons">
        <a href="#"><img src="../assets/index/index_qq.svg" alt="qq" width="25px"></a>
        <a href="#"><img src="../assets/index/index_github.svg" alt="github" width="25px"></a>
        <a href="#"><img src="../assets/index/index_email.svg" alt="email" width="25px"></a>
      </div>

      <div class="slider-navigation">
        <div class="nav-btn active"></div>
        <div class="nav-btn"></div>
      </div>
    </section>
  </div>
</template>

<script>
import '@/assets/index/index.css';
import * as js from '@/assets/index/index.js';

export default {
  name: 'Home',
  mounted() {
    js.scrollHeader();
  }
}
</script>