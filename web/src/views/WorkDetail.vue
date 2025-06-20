<template>
  <div class="work-detail">
    <h1>作品详情</h1>
    <h2>{{ work.w_name }}</h2>
    <p>{{ work.w_description }}</p>
    <a-button @click="goToWork">访问作品</a-button>
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
      <iframe :srcdoc="compiledContent" frameborder="0" title="作品预览"></iframe>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
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

const route = useRoute()
const id = route.params.id
const router = useRouter()
const work = ref({})
const userId = ref('')
const htmlContent = ref('')
const cssContent = ref('')
const jsContent = ref('')

// CodeMirror 扩展集
const baseExtensions = [
  basicSetup,
  githubLight,
  highlightActiveLine(),
  bracketMatching()
]
const htmlExtensions = [...baseExtensions, html()]
const cssExtensions = [...baseExtensions, css()]
const jsExtensions = [...baseExtensions, javascript()]

// 预览内容
const compiledContent = computed(() => `
  <base href="${config.API_BASE_URL}/api/work/file/${id}/">
  <style>${cssContent.value}</style>
  ${htmlContent.value}
  <script>${jsContent.value}<\/script>
`)

const token = sessionStorage.getItem('token')

onMounted(async () => {
  try {
    // 获取作品详情
    const detailRes = await request.get(`/api/work/detail/${id}`, {
      headers: { 'x-access-token': token }
    })
    if (detailRes.data.code === 200) {
      work.value = detailRes.data.data
    } else {
      message.error(detailRes.data.message || '获取作品详情失败')
    }

    // 获取 user_id
    const userRes = await request.get(`/api/user/get`, {
      headers: { 'x-access-token': token }
    })
    if (userRes.data.code === 200) {
      userId.value = userRes.data.data.user_id
    } else {
      message.error(userRes.data.message || '获取用户信息失败')
    }

    // 获取主文件内容
    const mainRes = await request.get(`/api/work/files/main/${id}`, {
      headers: { 'x-access-token': token }
    })
    if (mainRes.data.code === 200) {
      htmlContent.value = mainRes.data.data.html
      cssContent.value = mainRes.data.data.css
      jsContent.value = mainRes.data.data.javascript
    } else {
      message.error(mainRes.data.message || '获取文件内容失败')
    }
  } catch (error) {
    message.error(error.response?.data?.message || '请求失败')
  }
})

function goToWork() {
  const routeData = router.resolve(`/workpreview/${userId.value}/${id}`);
  window.open(routeData.href, '_blank');
}
</script>

<style scoped>
.work-detail {
  display: flex;
  flex-direction: column;
  padding: 0 20px;
  transition: 0.3s ease;
}

.work-detail h1 {
  margin-bottom: 20px;
}

.work-detail h2 {
  margin-bottom: 20px;
}

/* 三栏编辑器 */
.editor-container {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.editor-block {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.editor-block label {
  font-weight: bold;
  margin-bottom: 5px;
}

/* 外层可拖拽区域 */
.resizable {
  width: 100%;
  resize: vertical;
  overflow: hidden;
  height: 200px;
  min-height: 250px;
}

/* CodeMirror 充满父容器并启用滚动 */
.code-editor {
  height: 100%;
}

:deep(.code-editor .cm-editor),
:deep(.code-editor .cm-scroller) {
  height: 100% !important;
  overflow: auto;
}

/* 预览区域 */
.preview {
  margin-top: 20px;
  position: relative;
  width: 100%;
  padding-bottom: 56.25%;
  height: 0;
}

.preview iframe {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 4px;
}

/* 小屏幕响应 */
@media screen and (max-width: 1080px) {
  .work-detail {
    padding: 20px;
  }

  .work-detail h1,
  .work-detail h2 {
    text-align: center;
  }

  .editor-container {
    flex-direction: column;
  }

  .editor-block {
    width: 100%;
    margin-bottom: 20px;
  }
}
</style>