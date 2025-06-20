<template>
  <div class="template-browser">
    <h1>浏览模板</h1>
    <h5>这里有一些模板，你可以预览它们，查看他们的源代码</h5>
    <div v-if="templates.length">
      <div class="template-container">
        <a-card v-for="template in templates" :key="template.t_id" hoverable style="width: 450px; margin: 10px; padding: 2px;"
          @click="goToDetail(template.t_id)">

          <template #cover>
            <img :alt="template.t_name" :src="getTemplateImage(template.t_id)" />
          </template>

          <a-card-meta :title="template.t_name">
            <template #description>{{ template.t_description }}</template>
          </a-card-meta>

        </a-card>
      </div>
    </div>
    <div v-else>
      <p>未找到模板</p>
    </div>
  </div>
</template>

<script>
import request from '@/utils/request'
import { message } from 'ant-design-vue';
import config from '@/config'

export default {
  data() {
    return {
      templates: []
    };
  },
  async created() {
    await this.fetchTemplates();
  },
  methods: {
    async fetchTemplates() {
      try {
        const response = await request.get('/api/template/list');
        if (response.data.code === 200) {
          this.templates = response.data.data.list;
        } else {
          message.error(response.data.message || '获取模板列表失败');
        }
      } catch (error) {
        message.error(error.response?.data?.message || '获取模板列表失败');
      }
    },
    getTemplateImage(t_id) {
      return `${config.API_BASE_URL}/api/template/file/${t_id}/index.jpg`;
    },
    goToDetail(t_id) {
      this.$router.push(`/templatedetail/${t_id}`);
    }
  }
};
</script>

<style>

.template-browser {
  transition: 0.3s ease;
  flex-direction: column;
  display: flex;
  padding: 0px 20px;
  background: url("../assets/template/template.png");
  background-size: 100%;
}

.template-browser h5 {
  padding: 20px 0px;
}


.template-container {
  display: block;
  text-align: center;
}


.template-container .ant-card {
  display: inline-block;
  margin: 10px;
  text-align: left;
}

.template-screenshot {
  width: 100%;
  height: auto;
}

@media (max-width:1080px) {

  .template-browser {
    display: flex;
    flex-direction: column;
    padding-top: 75px;
    transition: 0.3s ease;
  }

  .template-browser h1 {
    text-align: center;
    font-size: 2.5rem;
    margin: 0;
    padding: 0;
  }

  .template-browser h5 {
    text-align: center;
    font-size: 1rem;
    margin: 0;
    padding: 0;
  }

}
</style>