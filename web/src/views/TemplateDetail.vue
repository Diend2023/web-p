<template>
  <div class="template-detail">
    <h1>模板详情</h1>
    <h2>{{ template.t_name }}</h2>
    <p>{{ template.t_description }}</p>
    <a-button @click="goToTemplate">访问模板</a-button>
    <div class="editor-container">
      <div class="editor-block">
        <label>HTML Content</label>
        <div class="resizable">
          <Codemirror class="code-editor" v-model="htmlContent" :extensions="htmlExtensions" />
        </div>
      </div>
      <div class="editor-block">
        <label>CSS Content</label>
        <div class="resizable">
          <Codemirror class="code-editor" v-model="cssContent" :extensions="cssExtensions" />
        </div>
      </div>
      <div class="editor-block">
        <label>JavaScript Content</label>
        <div class="resizable">
          <Codemirror class="code-editor" v-model="jsContent" :extensions="jsExtensions" />
        </div>
      </div>
    </div>

    <div class="preview">
      <iframe :srcdoc="compiledContent" frameborder="0" :title="template.t_name"></iframe>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Codemirror } from 'vue-codemirror-next'
import { basicSetup } from '@codemirror/basic-setup'
import { html } from '@codemirror/lang-html'
import { css } from '@codemirror/lang-css'
import { javascript } from '@codemirror/lang-javascript'
import { githubLight } from '@uiw/codemirror-theme-github'
import { highlightActiveLine } from '@codemirror/view'
import { bracketMatching } from '@codemirror/matchbrackets'
import request from '@/utils/request'
import { message } from 'ant-design-vue'
import config from '@/config'

const router = useRouter()

const props = defineProps({
  id: String
})

const template = ref({})
const htmlContent = ref('')
const cssContent = ref('')
const jsContent = ref('')

// 为每种语言准备扩展
const htmlExtensions = [basicSetup, githubLight, highlightActiveLine(), bracketMatching(), html()]
const cssExtensions = [basicSetup, githubLight, highlightActiveLine(), bracketMatching(), css()]
const jsExtensions = [basicSetup, githubLight, highlightActiveLine(), bracketMatching(), javascript()]

// 生成 iframe 预览内容
const compiledContent = computed(() => `
  <base href="${config.API_BASE_URL}/api/template/file/${props.id}/">
  <style>${cssContent.value}</style>
  ${htmlContent.value}
  <script>${jsContent.value}<\/script>
`)

async function fetchTemplateFiles() {
  try {
    const response = await request.get(`/api/template/files/main/${props.id}`)
    if (response.data.code === 200) {
      htmlContent.value = response.data.data.html || ''
      cssContent.value = response.data.data.css || ''
      jsContent.value = response.data.data.javascript || ''
    } else {
      message.error(response.data.message || '获取模板文件失败')
    }
  } catch (error) {
    message.error(error.response?.data?.message || '获取模板文件失败')
  }
}

function goToTemplate() {
  const routeData = router.resolve(`/templatepreview/${props.id}`);
  window.open(routeData.href, '_blank');
}

onMounted(async () => {
  try {
    const response = await request.get(`/api/template/detail/${props.id}`)
    if (response.data.code === 200) {
      template.value = response.data.data
      await fetchTemplateFiles()
    } else {
      message.error(response.data.message || '获取模板详情失败')
    }
  } catch (error) {
    message.error(error.response?.data?.message || '获取模板详情失败')
  }
})
</script>

<style scoped>
.template-detail {
  display: flex;
  flex-direction: column;
  padding: 0 20px;
}

.editor-container {
  display: flex;
  gap: 15px;
  margin-bottom: 20px;
}

.editor-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.editor-container label {
  font-weight: bold;
  margin-bottom: 5px;
}

.resizable {
  /* 用户可以上下拖拽这个区域改变高度 */
  width: 100%;
  resize: vertical;
  overflow: auto;

  /* 初始高度／最小高度／最大高度都可以自定义 */
  height: 250px;
  min-height: 250px;
}

.code-editor {
  height: 100%;
}

:deep(.code-editor .cm-editor),
:deep(.code-editor .cm-scroller) {
  height: 100% !important;
  max-width: 100%;
  overflow: auto;
}

.preview {
  margin-top: 20px;
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  height: 0;
}

iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
}

@media screen and (max-width: 1080px) {
    /* 整体容器缩内边距 */
    .template-detail {
      padding: 20px;
    }
    /* 标题居中并加间距 */
    .template-detail h1 {
      margin-bottom: 16px;
      text-align: center;
    }
    .template-detail h2 {
      margin-bottom: 12px;
      text-align: center;
    }
    /* 编辑器区域改为上下排列 */
    .editor-container {
      flex-direction: column;
    }
    /* 每列铺满，并在下方留空隙 */
    .editor-block {
      width: 100%;
      margin-bottom: 20px;
    }
  }
</style>