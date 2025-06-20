<template>
  <a-modal v-model:visible="isVisible" title="编辑作品" @ok="handleOk" @cancel="handleCancel" width="60%">
    <a-form :model="formState" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
      <!-- 基本信息 -->
      <a-form-item label="名称" name="name" :rules="[{ required: true, message: '请输入作品名称' }]">
        <a-input v-model:value="formState.name" />
      </a-form-item>
      <a-form-item label="描述" name="description" :rules="[{ required: true, message: '请输入作品描述' }]">
        <a-input v-model:value="formState.description" />
      </a-form-item>
      <a-form-item label="模板" name="templateName">
        <a-input v-model:value="formState.templateName" disabled />
      </a-form-item>

      <!-- 主文件上传 -->
      <a-form-item label="HTML" name="html">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.html" :extensions="htmlExtensions" />
        </div>
        <a-upload :before-upload="beforeUploadHtml" @remove="clearHtml" :max-count="1">
          <a-button>上传 HTML 文件</a-button>
        </a-upload>
      </a-form-item>
      <a-form-item label="CSS" name="css">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.css" :extensions="cssExtensions" />
        </div>
        <a-upload :before-upload="beforeUploadCss" @remove="clearCss" :max-count="1">
          <a-button>上传 CSS 文件</a-button>
        </a-upload>
      </a-form-item>
      <a-form-item label="JavaScript" name="javascript">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.javascript" :extensions="jsExtensions" />
        </div>
        <a-upload :before-upload="beforeUploadJs" @remove="clearJs" :max-count="1">
          <a-button>上传 JavaScript 文件</a-button>
        </a-upload>
      </a-form-item>

      <!-- 其它文件上传：加载原有文件并支持内置删除修改 -->
      <a-form-item label="其它文件" name="otherFiles">
        <a-upload :fileList="formState.otherFiles" :before-upload="beforeUploadOther" @remove="clearOther"
          :show-upload-list="{ showDownloadIcon: true }" @download="downloadOtherFile" :max-count="999"
          :multiple="true">
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
import { ref, watch } from 'vue';
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
import config from '@/config';


const props = defineProps({
  w_id: {
    type: Number,
    default: 0
  }
});
const emit = defineEmits(['updated']);

// 控制模态框显示
const isVisible = ref(false);

// 表单数据，包括主文件和其它文件
const formState = ref({
  name: '',
  description: '',
  templateId: '',
  templateName: '',
  html: '',
  css: '',
  javascript: '',
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

// 加载作品详情、主文件及其它文件
const loadWorkData = async () => {
  if (!props.w_id) return;
  await Promise.all([
    fetchWorkDetail(),
    fetchMainFiles(),
    fetchOtherFiles()
  ]);
};

// 获取作品基本信息
const fetchWorkDetail = async () => {
  try {
    const res = await request.get(`/api/admin/work/get/${props.w_id}`, {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      const work = res.data.data;
      formState.value.name = work.w_name;
      formState.value.description = work.w_description;
      formState.value.templateId = work.t_id || '';
      if (work.t_id) {
        const tplRes = await request.get(`/api/template/detail/${work.t_id}`);
        formState.value.templateName =
          (tplRes.data.code === 200 && tplRes.data.data.t_name) || '';
      } else {
        formState.value.templateName = '';
      }
    } else {
      message.error(res.data.message);
    }
  } catch (err) {
    message.error(err.response?.data?.message || '获取作品详情失败');
  }
};

// 获取主文件信息
const fetchMainFiles = async () => {
  try {
    const res = await request.get(`/api/admin/work/files/main/${props.w_id}`, {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      const mainFiles = res.data.data;
      formState.value.html = mainFiles.html;
      formState.value.css = mainFiles.css;
      formState.value.javascript = mainFiles.javascript;
    } else {
      message.error(res.data.message);
    }
  } catch (err) {
    message.error(err.response?.data?.message || '获取作品主文件失败');
  }
};

// 获取其它文件，并转换成 Upload 所需的 fileList 格式
const fetchOtherFiles = async () => {
  try {
    const res = await request.get(`/api/admin/work/files/other/${props.w_id}`, {
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

// 监听 w_id 变化后加载数据
watch(() => props.w_id, (newVal) => {
  if (newVal) {
    loadWorkData();
  }
});

// 主文件上传，读取文本内容
const beforeUploadHtml = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    formState.value.html = e.target.result;
  };
  reader.readAsText(file);
  return false;
};
const beforeUploadCss = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    formState.value.css = e.target.result;
  };
  reader.readAsText(file);
  return false;
};
const beforeUploadJs = (file) => {
  const reader = new FileReader();
  reader.onload = (e) => {
    formState.value.javascript = e.target.result;
  };
  reader.readAsText(file);
  return false;
};

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
    // 直接使用后端下载接口
    window.open(`${config.API_BASE_URL}/api/admin/work/file/${props.w_id}/${file.name}`, '_blank');
  }
};

// 其它文件上传，将新上传文件加入 fileList 中
const beforeUploadOther = (file) => {
  formState.value.otherFiles.push({
    uid: file.uid,
    name: file.name,
    status: 'done',
    originFileObj: file
  });
  return false;
};

// 删除操作，Upload 内置 @remove 事件传入文件对象
const clearHtml = () => { formState.value.html = ''; };
const clearCss = () => { formState.value.css = ''; };
const clearJs = () => { formState.value.javascript = ''; };
const clearOther = (file) => {
  formState.value.otherFiles = formState.value.otherFiles.filter(f => f.uid !== file.uid);
};

const handleOk = async () => {
  if (!formState.value.password) {
    message.error('请输入管理员密码');
    return;
  }
  try {
    const encryptedPassword = CryptoJS.SHA256(formState.value.password).toString();
    const data = new FormData();
    data.append('w_id', props.w_id);
    data.append('workName', formState.value.name);
    data.append('workDescription', formState.value.description);
    data.append('templateId', formState.value.templateId);
    data.append('htmlContent', formState.value.html);
    data.append('cssContent', formState.value.css);
    data.append('jsContent', formState.value.javascript);
    data.append('password', encryptedPassword);

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
    
    const res = await request.post('/api/admin/work/set', data, {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      message.success('作品更新成功');
      emit('updated');
      isVisible.value = false;
    } else {
      message.error(res.data.message);
    }
  } catch (err) {
    message.error(err.response?.data?.message || '更新作品失败');
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