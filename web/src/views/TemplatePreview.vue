<template>
  <div id="template-preview-app">
    <iframe 
      :src="templateUrl" 
      frameborder="0"
      style="width: 100vw; height: 100vh; display: block;"
    ></iframe>
  </div>
</template>

<script>
import config from '@/config'

export default {
  name: 'TemplatePreview',
  computed: {
    templateUrl() {
      const id = this.$route.params.id || this.$route.query.id;
      if (id) {
        return `${config.API_BASE_URL}/api/template/file/${id}/index.html`;
      }
      return '';
    }
  },
  mounted() {
    // 隐藏body的滚动条
    document.body.style.overflow = 'hidden';
    document.body.style.margin = '0';
    document.body.style.padding = '0';
    
    // 隐藏App.vue中的header等元素
    const appElement = document.getElementById('app');
    if (appElement) {
      // 隐藏除了当前组件外的所有子元素
      Array.from(appElement.children).forEach(child => {
        if (!child.contains(this.$el)) {
          child.style.display = 'none';
        }
      });
    }
  },
  beforeUnmount() {
    // 恢复样式
    document.body.style.overflow = '';
    document.body.style.margin = '';
    document.body.style.padding = '';
    
    // 恢复隐藏的元素
    const appElement = document.getElementById('app');
    if (appElement) {
      Array.from(appElement.children).forEach(child => {
        child.style.display = '';
      });
    }
  }
}
</script>

<style scoped>
#template-preview-app {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  width: 100vw !important;
  height: 100vh !important;
  z-index: 9999 !important;
  background: white;
  margin: 0 !important;
  padding: 0 !important;
}
</style>

<style>
/* 全局样式，确保完全覆盖 */
body:has(#template-preview-app) {
  overflow: hidden !important;
  margin: 0 !important;
  padding: 0 !important;
}
</style>