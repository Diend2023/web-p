<template>
  <a-modal v-model:visible="isVisible" title="编辑模板" @ok="handleOk" @cancel="handleCancel" width="60%">
    <a-form :model="formState" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
      <a-form-item label="模板名称" name="t_name" :rules="[{ required: true, message: '请输入模板名称' }]">
        <a-input v-model:value="formState.t_name" />
      </a-form-item>
      <a-form-item label="模板描述" name="t_description" :rules="[{ required: true, message: '请输入模板描述' }]">
        <a-input v-model:value="formState.t_description" />
      </a-form-item>

      <a-form-item label="HTML" name="htmlContent">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.html" :extensions="htmlExtensions" />
        </div>
        <a-upload :before-upload="beforeUploadHtml" @remove="clearHtml" :max-count="1">
          <a-button>上传 HTML 文件</a-button>
        </a-upload>
      </a-form-item>

      <a-form-item label="CSS" name="cssContent">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.css" :extensions="cssExtensions" />
        </div>
        <a-upload :before-upload="beforeUploadCss" @remove="clearCss" :max-count="1">
          <a-button>上传 CSS 文件</a-button>
        </a-upload>
      </a-form-item>

      <a-form-item label="JavaScript" name="jsContent">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.js" :extensions="jsExtensions" />
        </div>
        <a-upload :before-upload="beforeUploadJs" @remove="clearJs" :max-count="1">
          <a-button>上传 JS 文件</a-button>
        </a-upload>
      </a-form-item>

      <a-form-item label="截图" name="screenshot">
        <a-upload list-type="picture-card" :file-list="formState.screenshot" :before-upload="beforeUploadScreenshot"
          @remove="clearScreenshot" accept="image/jpeg" :max-count="1">
          <div>
            <PlusOutlined />
            <div style="margin-top: 8px">Upload</div>
          </div>
        </a-upload>
      </a-form-item>

      <a-form-item label="其它文件" name="otherFiles">
        <a-upload :file-list="formState.otherFiles" :before-upload="beforeUploadOther" @remove="clearOther"
          :show-upload-list="{ showDownloadIcon: true }" @download="downloadOtherFile" multiple :max-count="999">
          <a-button>上传其它文件</a-button>
        </a-upload>
      </a-form-item>

      <a-form-item label="管理员密码" name="password" :rules="[{ required: true, message: '请输入管理员密码' }]">
        <a-input type="password" v-model:value="formState.password" />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup>
import { ref, watch } from 'vue'
import request from '@/utils/request'
import { message } from 'ant-design-vue'
import CryptoJS from 'crypto-js'
import { Codemirror } from 'vue-codemirror-next'
import { basicSetup } from '@codemirror/basic-setup'
import { html } from '@codemirror/lang-html'
import { css } from '@codemirror/lang-css'
import { javascript } from '@codemirror/lang-javascript'
import { githubLight } from '@uiw/codemirror-theme-github'
import { highlightActiveLine } from '@codemirror/view'
import { bracketMatching } from '@codemirror/matchbrackets'
import config from '@/config'

const props = defineProps({
  t_id: { type: Number, default: 0 }
})
const emit = defineEmits(['updated'])

const isVisible = ref(false)
const formState = ref({
  t_name: '',
  t_description: '',
  html: '',
  css: '',
  js: '',
  screenshot: [],
  otherFiles: [],
  password: ''
})

const baseExtensions = [
  basicSetup,
  githubLight,
  highlightActiveLine(),
  bracketMatching()
]
const htmlExtensions = [...baseExtensions, html()]
const cssExtensions = [...baseExtensions, css()]
const jsExtensions = [...baseExtensions, javascript()]

const token = sessionStorage.getItem('adminToken')

watch(isVisible, visible => {
  if (!visible) {
    formState.value.password = ''
  }
})

// 加载模板详情、主文件、其它文件
const loadTemplateData = async () => {
  if (!props.t_id) return
  await Promise.all([fetchDetail(), fetchMainFiles(), fetchOtherFiles()])
}

const fetchDetail = async () => {
  try {
    const res = await request.get(`/api/admin/template/get/${props.t_id}`, {
      headers: { 'x-access-token': token }
    })
    if (res.data.code === 200) {
      formState.value.t_name = res.data.data.t_name
      formState.value.t_description = res.data.data.t_description
    } else {
      message.error(res.data.message)
    }
  } catch {
    message.error('获取模板详情失败')
  }
}

const fetchMainFiles = async () => {
  try {
    const res = await request.get(`/api/admin/template/files/main/${props.t_id}`, {
      headers: { 'x-access-token': token }
    })
    if (res.data.code === 200) {
      const d = res.data.data
      formState.value.html = d.html || ''
      formState.value.css = d.css || ''
      formState.value.js = d.javascript || ''
      formState.value.screenshot = d.screenshot
        ? [{
          uid: 'old_screenshot',
          name: d.screenshot.split('/').pop(),
          status: 'done',
          url: d.screenshot,
          response: { file_content: d.screenshot }
        }]
        : []
    } else {
      message.error(res.data.message)
    }
  } catch {
    message.error('获取模板主文件失败')
  }
}

// 下载截图
const downloadScreenshot = file => {
  if (file.originFileObj) {
    // 新上传文件保持不变
    const url = URL.createObjectURL(file.originFileObj);
    const a = document.createElement('a');
    a.href = url; a.download = file.name;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } else if (file.response?.file_content) {
    // 后端返回的 Base64 data URI
    const dataUri = file.response.file_content;
    const matched = dataUri.match(/^data:(.+);base64,(.*)$/);
    if (!matched) return message.error('无法解析文件内容');
    const mime = matched[1], b64 = matched[2];
    const binStr = atob(b64);
    const len = binStr.length;
    const arr = new Uint8Array(len);
    for (let i = 0; i < len; i++) arr[i] = binStr.charCodeAt(i);
    const blob = new Blob([arr], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = file.name;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } else {
    window.open(`${config.API_BASE_URL}/api/admin/template/file/${props.t_id}/${file.name}`, '_blank')
  }
}

const fetchOtherFiles = async () => {
  try {
    const res = await request.get(`/api/admin/template/files/other/${props.t_id}`, {
      headers: { 'x-access-token': token }
    });
    let filesData = [];
    if (Array.isArray(res.data)) {
      filesData = res.data;
    } else if (res.data && Array.isArray(res.data.data)) {
      filesData = res.data.data;
    } else if (typeof res.data === "string") {
      try {
        filesData = JSON.parse(res.data);
        if (!Array.isArray(filesData)) filesData = [];
      } catch (e) {
        message.error("解析其它文件数据失败");
        filesData = [];
      }
    }
    // 将返回的其它文件组装成 fileList 对象（这里加入 uid、name、status 和 response 保存原始内容）
    formState.value.otherFiles = filesData.map((item, index) => ({
      uid: `old_${index}`,
      name: item.filename || '未命名',
      status: 'done',
      response: { file_content: item.file_content || '' }
    }));
  } catch (err) {
    message.error(err.response?.data?.message || "获取作品其它文件失败");
    formState.value.otherFiles = [];
  }
};

watch(() => props.t_id, () => {
  if (props.t_id) loadTemplateData()
})

// 上传/清除 HTML/CSS/JS
const beforeUploadHtml = file => {
  const reader = new FileReader()
  reader.onload = e => { formState.value.html = e.target.result }
  reader.readAsText(file)
  return false
}
const clearHtml = () => { formState.value.html = '' }

const beforeUploadCss = file => {
  const reader = new FileReader()
  reader.onload = e => { formState.value.css = e.target.result }
  reader.readAsText(file)
  return false
}
const clearCss = () => { formState.value.css = '' }

const beforeUploadJs = file => {
  const reader = new FileReader()
  reader.onload = e => { formState.value.js = e.target.result }
  reader.readAsText(file)
  return false
}
const clearJs = () => { formState.value.js = '' }

// 上传/清除 截图
const beforeUploadScreenshot = file => {
  formState.value.screenshot = [{
    uid: file.uid,
    name: file.name,
    status: 'done',
    originFileObj: file
  }]
  return false
}
const clearScreenshot = () => {
  formState.value.screenshot = []
}


// 上传/清除 其它文件
const beforeUploadOther = file => {
  formState.value.otherFiles.push({ uid: file.uid, name: file.name, status: 'done', originFileObj: file })
  return false
}
const clearOther = file => {
  formState.value.otherFiles = formState.value.otherFiles.filter(f => f.uid !== file.uid)
}

// 下载已选文件
const downloadOtherFile = (file) => {
  if (file.originFileObj) {
    // 新上传文件保持不变
    const url = URL.createObjectURL(file.originFileObj);
    const a = document.createElement('a');
    a.href = url; a.download = file.name;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } else if (file.response?.file_content) {
    // 后端返回的 Base64 data URI
    const dataUri = file.response.file_content;
    const matched = dataUri.match(/^data:(.+);base64,(.*)$/);
    if (!matched) return message.error('无法解析文件内容');
    const mime = matched[1], b64 = matched[2];
    const binStr = atob(b64);
    const len = binStr.length;
    const arr = new Uint8Array(len);
    for (let i = 0; i < len; i++) arr[i] = binStr.charCodeAt(i);
    const blob = new Blob([arr], { type: mime });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = file.name;
    document.body.appendChild(a); a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  } else {
    window.open(`${config.API_BASE_URL}/api/admin/template/file/${props.t_id}/${file.name}`, '_blank')
  }
}

// 提交更新
const handleOk = async () => {
  if (!formState.value.password) {
    return message.error('请输入管理员密码')
  }
  if (formState.value.screenshot.length === 0) {
    return message.error('请上传截图')
  }
  try {
    const data = new FormData()
    const encryptedPassword = CryptoJS.SHA256(formState.value.password).toString()
    data.append('t_id', props.t_id)
    data.append('t_name', formState.value.t_name)
    data.append('t_description', formState.value.t_description)
    data.append('htmlContent', formState.value.html)
    data.append('cssContent', formState.value.css)
    data.append('jsContent', formState.value.js)
    data.append('password', encryptedPassword)

    formState.value.screenshot.forEach(file => {
      if (file.originFileObj) {
        data.append('screenshot', file.originFileObj, file.name);
      } else if (file.response && file.response.file_content) {
        const match = file.response.file_content.match(/^data:(.+);base64,(.+)$/);
        if (match) {
          const mime = match[1], b64 = match[2];
          const bin = atob(b64);
          const arr = new Uint8Array(bin.length);
          for (let i = 0; i < bin.length; i++) {
            arr[i] = bin.charCodeAt(i);
          }
          const blob = new Blob([arr], { type: mime });
          data.append('screenshot', blob, file.name);
        }
      }
    });

    formState.value.otherFiles.forEach(file => {
      if (file.originFileObj) {
        data.append('otherFiles', file.originFileObj, file.name);
      } else if (file.response && file.response.file_content) {
        const match = file.response.file_content.match(/^data:(.+);base64,(.+)$/);
        if (match) {
          const mime = match[1], b64 = match[2];
          const bin = atob(b64);
          const arr = new Uint8Array(bin.length);
          for (let i = 0; i < bin.length; i++) {
            arr[i] = bin.charCodeAt(i);
          }
          const blob = new Blob([arr], { type: mime });
          data.append('otherFiles', blob, file.name);
        }
      }
    });

    const res = await request.post('/api/admin/template/set', data, {
      headers: { 'x-access-token': token }
    })
    if (res.data.code === 200) {
      message.success('模板更新成功')
      emit('updated')
      isVisible.value = false
    } else {
      message.error(res.data.message)
    }
  } catch {
    message.error('更新模板失败')
  }
}

const handleCancel = () => {
  isVisible.value = false
}

defineExpose({ isVisible })
</script>

<style scoped>
.resizable {
  width: 100%;
  resize: vertical;
  overflow: hidden;
  height: 200px;
  min-height: 200px;
}

.code-editor {
  height: 100%;
}

:deep(.code-editor .cm-editor),
:deep(.code-editor .cm-scroller) {
  height: 100% !important;
  overflow: auto;
}
</style>