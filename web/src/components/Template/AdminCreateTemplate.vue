<template>
  <a-modal v-model:visible="isVisible" title="创建模板" @ok="handleOk" @cancel="handleCancel" width="60%">
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
          :show-upload-list="{ showDownloadIcon: true }" @download="downloadFile" multiple :max-count="999">
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
import { ref } from 'vue';
import request from '@/utils/request'
import { message } from 'ant-design-vue';
import CryptoJS from 'crypto-js';
import { Codemirror } from 'vue-codemirror-next';
import { basicSetup } from '@codemirror/basic-setup';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { javascript } from '@codemirror/lang-javascript';
import { githubLight } from '@uiw/codemirror-theme-github';
import { highlightActiveLine } from '@codemirror/view';
import { bracketMatching } from '@codemirror/matchbrackets';

const isVisible = ref(false);
const formState = ref({
  t_name: '',
  t_description: '',
  html: '',
  css: '',
  js: '',
  screenshot: [],
  otherFiles: [],
  password: ''
});

const baseExtensions = [
  basicSetup,
  githubLight,
  highlightActiveLine(),
  bracketMatching()
];
const htmlExtensions = [...baseExtensions, html()];
const cssExtensions = [...baseExtensions, css()];
const jsExtensions = [...baseExtensions, javascript()];

const token = sessionStorage.getItem('adminToken');
const emit = defineEmits(['created']);

// 上传/删除 逻辑
const beforeUploadHtml = file => {
  const reader = new FileReader();
  reader.onload = e => { formState.value.html = e.target.result; };
  reader.readAsText(file);
  return false;
};
const clearHtml = () => { formState.value.html = ''; };

const beforeUploadCss = file => {
  const reader = new FileReader();
  reader.onload = e => { formState.value.css = e.target.result; };
  reader.readAsText(file);
  return false;
};
const clearCss = () => { formState.value.css = ''; };

const beforeUploadJs = file => {
  const reader = new FileReader();
  reader.onload = e => { formState.value.js = e.target.result; };
  reader.readAsText(file);
  return false;
};
const clearJs = () => { formState.value.js = ''; };

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

const beforeUploadOther = file => {
  formState.value.otherFiles.push({ uid: file.uid, name: file.name, status: 'done', originFileObj: file })
  return false
}
const clearOther = file => {
  formState.value.otherFiles = formState.value.otherFiles.filter(f => f.uid !== file.uid)
}

const downloadFile = file => {
  const blob = file.originFileObj || file;
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = file.name;
  document.body.appendChild(a); a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

// 提交
const handleOk = async () => {
  if (!formState.value.t_name || !formState.value.t_description || !formState.value.password) {
    return message.error('名称、描述和密码不能为空');
  }
  try {
    const data = new FormData();
    const encryptedPassword = CryptoJS.SHA256(formState.value.password).toString();
    data.append('t_name', formState.value.t_name);
    data.append('t_description', formState.value.t_description);
    data.append('htmlContent', formState.value.html);
    data.append('cssContent', formState.value.css);
    data.append('jsContent', formState.value.js);
    data.append('password', encryptedPassword);

    formState.value.screenshot.forEach(file => {
      if (file.originFileObj) {
        data.append('screenshot', file.originFileObj, file.name);
      } else if (file.response && file.response.file_content) {
        const blob = new Blob([file.response.file_content], { type: 'text/plain' });
        data.append('screenshot', blob, file.name);
      }
    });

    formState.value.otherFiles.forEach(file => {
      if (file.originFileObj) {
        data.append('otherFiles', file.originFileObj, file.name);
      } else if (file.response && file.response.file_content) {
        const blob = new Blob([file.response.file_content], { type: 'text/plain' });
        data.append('otherFiles', blob, file.name);
      }
    });

    const res = await request.post('/api/admin/template/create', data, {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      message.success('创建模板成功');
      emit('created');
      isVisible.value = false;
      // 重置
      formState.value = {
        t_name: '', t_description: '',
        html: '', css: '', js: '',
        screenshot: [], otherFiles: [], password: ''
      };
    } else {
      message.error(res.data.message);
    }
  } catch (err) {
    message.error(err.response?.data?.message || '创建模板失败');
    message.error(err.message);
  }
};

const handleCancel = () => {
  isVisible.value = false;
};

defineExpose({ isVisible });
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