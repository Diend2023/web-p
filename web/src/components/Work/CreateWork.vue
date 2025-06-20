<template>
  <a-modal v-model:visible="isVisible" title="创建新作品" @ok="handleOk" @cancel="handleCancel" width="60%">
    <a-form :model="formState" :label-col="{ span: 4 }" :wrapper-col="{ span: 18 }">
      <a-form-item label="名称" name="name" :rules="[{ required: true, message: '请输入作品名称' }]">
        <a-input v-model:value="formState.name" />
      </a-form-item>
      <a-form-item label="描述" name="description" :rules="[{ required: true, message: '请输入作品描述' }]">
        <a-input v-model:value="formState.description" />
      </a-form-item>
      <a-form-item label="模板" name="templateName">
        <a-input v-model:value="formState.templateName" disabled />
        <a-button type="primary" @click="showTemplateModal">选择模板</a-button>
        <a-button type="default" @click="clearTemplateSelection">取消选择</a-button>
      </a-form-item>
      <a-form-item label="HTML" name="html">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.html" :extensions="htmlExtensions"
            :disabled="!!formState.templateId" />
        </div>
        <a-upload :disabled="!!formState.templateId" :before-upload="beforeUploadHtml" @remove="clearHtml"
          :max-count="1">
          <a-button :disabled="!!formState.templateId">上传 HTML 文件</a-button>
        </a-upload>
      </a-form-item>
      <a-form-item label="CSS" name="css">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.css" :extensions="cssExtensions"
            :disabled="!!formState.templateId" />
        </div>
        <a-upload :disabled="!!formState.templateId" :before-upload="beforeUploadCss" @remove="clearCss" :max-count="1">
          <a-button :disabled="!!formState.templateId">上传 CSS 文件</a-button>
        </a-upload>
      </a-form-item>
      <a-form-item label="JavaScript" name="javascript">
        <div class="resizable">
          <Codemirror class="code-editor" v-model="formState.javascript" :extensions="jsExtensions"
            :disabled="!!formState.templateId" />
        </div>
        <a-upload :disabled="!!formState.templateId" :before-upload="beforeUploadJs" @remove="clearJs" :max-count="1">
          <a-button :disabled="!!formState.templateId">上传 JavaScript 文件</a-button>
        </a-upload>
      </a-form-item>
      <a-form-item label="其它文件" name="otherFiles">
        <a-upload :fileList="formState.otherFiles" :before-upload="beforeUploadOther" @remove="clearOther"
          :show-upload-list="{ showDownloadIcon: true }" @download="downloadOtherFile" :max-count="999"
          :multiple="true">
          <a-button :disabled="!!formState.templateId">上传其它文件</a-button>
        </a-upload>
      </a-form-item>
    </a-form>
  </a-modal>

  <a-modal v-model:visible="isTemplateModalVisible" title="选择模板" @ok="handleTemplateOk" @cancel="handleTemplateCancel"
    width="80%">
    <a-table :columns="templateColumns" :data-source="templates" rowKey="t_id" size="middle">
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'select'">
          <a-radio :checked="selectedTemplate && selectedTemplate.t_id === record.t_id"
            @change="selectTemplate(record)" />
        </template>
        <template v-else-if="column.dataIndex === 't_name'">
          <a @click="goToTemplateDetail(record.t_id)" style="cursor:pointer; color:#1890ff">
            {{ record.t_name }}
          </a>
        </template>
        <template v-else-if="column.dataIndex === 't_description'">
          {{ record.t_description }}
        </template>
        <template v-else-if="column.key === 'preview'">
          <img :src="getTemplateImageUrl(record.t_id)" alt="预览图" style="width:200px; height:auto;" />
        </template>
      </template>
    </a-table>
  </a-modal>
</template>

<script setup>
import { ref } from 'vue';
import request from '@/utils/request'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue';
import { Codemirror } from 'vue-codemirror-next';
import { basicSetup } from '@codemirror/basic-setup';
import { html } from '@codemirror/lang-html';
import { css } from '@codemirror/lang-css';
import { javascript } from '@codemirror/lang-javascript';
import { githubLight } from '@uiw/codemirror-theme-github';
import { highlightActiveLine } from '@codemirror/view';
import { bracketMatching } from '@codemirror/matchbrackets';
import config from '@/config';

const router = useRouter();

const isVisible = ref(false);
const isTemplateModalVisible = ref(false);
const formState = ref({
  name: '',
  description: '',
  templateId: '',
  templateName: '',
  html: '',
  css: '',
  javascript: '',
  otherFiles: []  // 这里存放上传的文件对象
});
const templates = ref([]);
const selectedTemplate = ref(null);

const emit = defineEmits(['created']);

const baseExtensions = [
  basicSetup,
  githubLight,
  highlightActiveLine(),
  bracketMatching()
];
const htmlExtensions = [...baseExtensions, html()];
const cssExtensions = [...baseExtensions, css()];
const jsExtensions = [...baseExtensions, javascript()];

const goToTemplateDetail = (t_id) => {
  const routeData = router.resolve(`/templatedetail/${t_id}`);
  window.open(routeData.href, '_blank');
};

const getTemplateImageUrl = (templateId) => {
  return `${config.API_BASE_URL}/api/template/file/${templateId}/index.jpg`;
};

const fetchTemplates = async () => {
  try {
    const response = await request.get('/api/template/list');
    if (response.data.code === 200 || response.data.code === 201) {
      templates.value = response.data.data.list;
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
  }
};

const handleOk = async () => {
  try {
    const token = sessionStorage.getItem('token');
    // 使用 FormData 构造多部分数据
    const data = new FormData();
    data.append('workName', formState.value.name);
    data.append('workDescription', formState.value.description);
    data.append('templateId', formState.value.templateId);
    data.append('htmlContent', formState.value.html);
    data.append('cssContent', formState.value.css);
    data.append('jsContent', formState.value.javascript);
    // 遍历其它文件，将每个文件对象添加到 FormData 中
    formState.value.otherFiles.forEach(file => {
      data.append('otherFiles', file, file.name);
    });

    const response = await request.post('/api/work/create', data, {
      headers: {
        'x-access-token': token
        // 'Content-Type': 'multipart/form-data'
      }
    });
    if (response.data.code === 200 || response.data.code === 201) {
      message.success('作品创建成功');
      emit('created');
      isVisible.value = false;
      // 重置表单
      formState.value = {
        name: '',
        description: '',
        templateId: '',
        templateName: '',
        html: '',
        css: '',
        javascript: '',
        otherFiles: []
      };
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(error.response.data.message ? error.response.data.message : '未知错误，请联系管理员');
  }
};

const handleCancel = () => {
  isVisible.value = false;
};

const showTemplateModal = () => {
  isTemplateModalVisible.value = true;
  fetchTemplates();
};

const handleTemplateOk = () => {
  if (selectedTemplate.value) {
    formState.value.templateId = selectedTemplate.value.t_id;
    formState.value.templateName = selectedTemplate.value.t_name;
  }
  isTemplateModalVisible.value = false;
};

const handleTemplateCancel = () => {
  isTemplateModalVisible.value = false;
};

const clearTemplateSelection = () => {
  selectedTemplate.value = null;
  formState.value.templateId = '';
  formState.value.templateName = '';
};

const selectTemplate = (record) => {
  selectedTemplate.value = record;
};

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
  // file.originFileObj 为新上传文件的原始 File 对象
  const blob = file.originFileObj || file;
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = file.name;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
};

const beforeUploadOther = (file) => {
  formState.value.otherFiles.push({
    uid: file.uid,
    name: file.name,
    status: 'done',
    originFileObj: file
  });
  return false;
};

const clearHtml = () => {
  formState.value.html = '';
};

const clearCss = () => {
  formState.value.css = '';
};

const clearJs = () => {
  formState.value.javascript = '';
};

const clearOther = (file) => {
  formState.value.otherFiles = formState.value.otherFiles.filter(f => f.uid !== file.uid);
};

const templateColumns = [
  {
    title: '选择',
    key: 'select',
    width: '5%',
  },
  {
    title: '模板ID',
    dataIndex: 't_id',
    key: 't_id',
    width: '10%',
  },
  {
    title: '模板名称',
    dataIndex: 't_name',
    key: 't_name',
    width: '20%',
  },
  {
    title: '模板介绍',
    dataIndex: 't_description',
    key: 't_description',
    width: '50%',
  },
  {
    title: '预览图',
    key: 'preview',
    width: '15%',
  },
];

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