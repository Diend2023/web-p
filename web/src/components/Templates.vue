<template>
  <div class="context_box">
    <a-form layout="inline" :model="filters" class="search-form">
      <a-button type="primary" class="create-template" @click="showCreateTemplateModal">
        创建模板
      </a-button>
      <a-form-item label="ID">
        <a-input v-model:value="filters.t_id" placeholder="模板id" style="width:100px" />
      </a-form-item>
      <a-form-item label="作者">
        <a-input v-model:value="filters.t_author" placeholder="模板作者" style="width:160px" />
      </a-form-item>
      <a-form-item label="名称">
        <a-input v-model:value="filters.t_name" placeholder="模板名称" style="width:180px" />
      </a-form-item>
      <a-form-item label="描述">
        <a-input v-model:value="filters.t_description" placeholder="模板描述" style="width:200px" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="onSearch">搜索</a-button>
        <a-button class="reset-btn" @click="onReset">重置</a-button>
      </a-form-item>
    </a-form>

    <AdminCreateTemplate ref="createTemplateModal" @created="fetchTemplates" />
    <AdminChangeTemplate :t_id="currentEditId" ref="changeTemplateModal" @updated="fetchTemplates" />

    <a-table :columns="columns" :data-source="templates.list" :pagination="pagination" @change="handleTableChange"
      rowKey="t_id" size="middle" :scroll="{ x: 800 }">
      <template #bodyCell="{ column, record }">
        <!-- 模板名称可点击跳转 -->
        <template v-if="column.key === 't_name'">
          <a @click="goToTemplateDetail(record.t_id)" style="cursor:pointer; color:#1890ff">
            {{ record.t_name }}
          </a>
        </template>
        <span v-else-if="column.dataIndex">
          {{ record[column.dataIndex] }}
        </span>
        <template v-else-if="column.key === 'action'">
          <a @click="handleEdit(record)">编辑</a>
          <a-divider type="vertical" />
          <a @click="handleDelete(record)">删除</a>
        </template>
      </template>
    </a-table>
    <a-modal v-model:visible="isDeleteTemplateModalVisible" title="确认删除模板" @ok="handleDeleteTemplateOk"
      @cancel="handleDeleteTemplateCancel">
      <a-form :model="deleteForm">
        <a-form-item label="验证信息" name="verification"
          :help="currentDeleteTemplate ? `请输入“确认删除${currentDeleteTemplate.t_name}”` : ''" :rules="[{ required: true }]">
          <a-input v-model:value="deleteForm.verification" />
        </a-form-item>
        <a-form-item label="管理员密码" name="password" :rules="[{ required: true, message: '请输入管理员密码' }]">
          <a-input-password v-model:value="deleteForm.password" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import { useRouter } from 'vue-router';
import request from '@/utils/request'
import { message } from 'ant-design-vue';
import CryptoJS from 'crypto-js'
import AdminCreateTemplate from '@/components/Template/AdminCreateTemplate.vue';
import AdminChangeTemplate from '@/components/Template/AdminChangeTemplate.vue';

const templates = ref({ list: [], total: 0 });
const filters = ref({
  t_id: '', t_author: '', t_name: '', t_description: ''
});
const pagination = ref({
  current: 1, pageSize: 10, total: 0,
  showSizeChanger: true, showQuickJumper: true,
  showTotal: t => `共 ${t} 条`
});
const token = sessionStorage.getItem('adminToken');
const router = useRouter();

const createTemplateModal = ref(null);
const changeTemplateModal = ref(null);
const currentEditId = ref(0)

const isDeleteTemplateModalVisible = ref(false)
const deleteForm = reactive({ verification: '', password: '' })
const currentDeleteTemplate = ref(null)

const showCreateTemplateModal = () => {
  createTemplateModal.value.isVisible = true;
};

const handleEdit = record => {
  currentEditId.value = record.t_id
  changeTemplateModal.value.isVisible = true
}

const handleDelete = record => {
  currentDeleteTemplate.value = record
  deleteForm.verification = ''
  deleteForm.password = ''
  isDeleteTemplateModalVisible.value = true
}

// 确认删除
const handleDeleteTemplateOk = async () => {
  if (!deleteForm.password) {
    message.error('请输入管理员密码')
    return
  }
  if (deleteForm.verification !== `确认删除${currentDeleteTemplate.value.t_name}`) {
    message.error(`请输入“确认删除${currentDeleteTemplate.value.t_name}”`)
    return
  }
  try {
    const hashedPwd = CryptoJS.SHA256(deleteForm.password).toString()
    const res = await request.post(
      '/api/admin/template/del',
      { t_id: currentDeleteTemplate.value.t_id, password: hashedPwd },  // 附带密码
      { headers: { 'x-access-token': token } }
    )
    if (res.data.code === 200 || res.data.code === 201) {
      message.success(res.data.message)
      fetchTemplates()
    } else {
      message.error(res.data.message)
    }
  } catch (err) {
    message.error(err.response?.data?.message || '删除模板失败')
  }
  // 重置状态
  isDeleteTemplateModalVisible.value = false
  currentDeleteTemplate.value = null
}

const handleDeleteTemplateCancel = () => {
  isDeleteTemplateModalVisible.value = false
  currentDeleteTemplate.value = null
}

const goToTemplateDetail = (t_id) => {
  router.push(`/templatedetail/${t_id}`);
};

const fetchTemplates = async () => {
  try {
    const { current, pageSize } = pagination.value;
    const params = {
      page: current, size: pageSize,
      ...(filters.value.t_id && { t_id: Number(filters.value.t_id) }),
      ...(filters.value.t_author && { t_author: filters.value.t_author }),
      ...(filters.value.t_name && { t_name: filters.value.t_name }),
      ...(filters.value.t_description && { t_description: filters.value.t_description })
    };
    const res = await request.get('/api/admin/template/list', {
      params, headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      templates.value = res.data.data;
      pagination.value.total = res.data.data.total;
    } else {
      message.error(res.data.message);
    }
  } catch {
    message.error('获取模板列表失败');
  }
};

const handleTableChange = ({ current, pageSize }) => {
  pagination.value.current = current;
  pagination.value.pageSize = pageSize;
  fetchTemplates();
};
const onSearch = () => { pagination.value.current = 1; fetchTemplates(); };
const onReset = () => {
  filters.value = { t_id: '', t_author: '', t_name: '', t_description: '' };
  pagination.value.current = 1; fetchTemplates();
};

onMounted(fetchTemplates);

// 表格列
const columns = [
  { title: '模板ID', dataIndex: 't_id', key: 't_id', width: 80, fixed: 'left' },
  { title: '作者', dataIndex: 't_author', key: 't_author', width: 160, ellipsis: true },
  { title: '名称', dataIndex: 't_name', key: 't_name', width: 180, ellipsis: true },
  { title: '描述', dataIndex: 't_description', key: 't_description', ellipsis: true },
  { title: '操作', key: 'action', width: 120, fixed: 'right' }
];
</script>

<style scoped>
.search-form {
  margin-bottom: 16px;
}

.create-template {
  margin-right: 8px;
}

.reset-btn {
  margin-left: 8px;
}

.context_box {
  min-height: 100vh;
  width: 100%;
  padding: 20px;
  background: #f5f5f5;
}

@media screen and (max-width: 1080px) {
  .context_box {
    padding: 10px;
  }
}

@media screen and (max-width: 768px) {
  .context_box {
    padding: 5px;
  }
}
</style>