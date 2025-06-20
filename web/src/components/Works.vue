<template>
  <div class="context_box">
    <a-form layout="inline" :model="filters" class="search-form">
      <a-form-item label="作品id">
        <a-input v-model:value="filters.w_id" placeholder="作品id" style="width:100px" />
      </a-form-item>
      <a-form-item label="用户id">
        <a-input v-model:value="filters.u_id" placeholder="用户id" style="width:100px" />
      </a-form-item>
      <a-form-item label="作品名称">
        <a-input v-model:value="filters.w_name" placeholder="作品名称" style="width:180px" />
      </a-form-item>
      <a-form-item label="作品描述">
        <a-input v-model:value="filters.w_description" placeholder="作品描述" style="width:200px" />
      </a-form-item>
      <a-form-item label="使用模板">
        <a-select v-model:value="filters.t_id" placeholder="选择模板" style="width:160px" allowClear>
          <a-select-option v-for="tpl in templates" :key="tpl.t_id" :value="tpl.t_id">
            {{ tpl.t_name }}
          </a-select-option>
        </a-select>
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="onSearch">搜索</a-button>
        <a-button class="reset-btn" @click="onReset">重置</a-button>
      </a-form-item>
    </a-form>
    <!-- 作品列表表格 -->
    <a-table :columns="columns" :data-source="works.list" :pagination="pagination" @change="handleTableChange"
      rowKey="w_id" size="middle" :scroll="{ x: 800 }">
      <template #bodyCell="{ column, record }">
        <!-- 作品名称：点击跳转详情 -->
        <template v-if="column.key === 'w_name'">
          <a @click="goToWorkDetail(record.w_id)">{{ record.w_name }}</a>
        </template>
        <!-- 作品描述 -->
        <template v-else-if="column.key === 'w_description'">
          <span>{{ record.w_description }}</span>
        </template>
        <!-- 模板名称：点击跳转模板详情 -->
        <template v-else-if="column.key === 't_name'">
          <a @click="goToTemplateDetail(record.t_id)" target="_blank">{{ record.t_name }}</a>
        </template>
        <!-- 操作列：提供编辑和删除 -->
        <template v-else-if="column.key === 'action'">
          <span>
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a @click="handleDelete(record)">删除</a>
          </span>
        </template>
      </template>
    </a-table>

    <!-- 编辑作品弹窗 -->
    <ChangeWork :w_id="currentEditId" ref="changeWorkModal" @updated="fetchWorks" />

    <!-- 删除确认弹窗：要求输入验证信息 -->
    <a-modal v-model:visible="isDeleteWorkModalVisible" title="确认删除作品" @ok="handleDeleteWorkOk"
      @cancel="handleDeleteWorkCancel">
      <a-form :model="deleteForm">
        <a-form-item label="验证信息" name="verification"
          :help="currentDeleteWork ? `请输入“确认删除${currentDeleteWork.w_name}”` : ''" :rules="[{ required: true }]">
          <a-input v-model:value="deleteForm.verification" />
        </a-form-item>
        <a-form-item label="管理员密码" name="password" :rules="[{ required: true, message: '请输入管理员密码' }]">
          <a-input type="password" v-model:value="deleteForm.password" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import request from '@/utils/request'
import { message } from 'ant-design-vue';
import CryptoJS from 'crypto-js'
import { useRouter } from 'vue-router';
import ChangeWork from '@/components/Work/AdminChangeWork.vue';

const works = ref([]);
const templates = ref([]);
const filters = ref({ w_id: '', u_id: '', w_name: '', w_description: '', t_id: null });
const pagination = ref({
  current: 1, pageSize: 10, total: 0,
  showSizeChanger: true, showQuickJumper: true,
  showTotal: t => `共 ${t} 条`
});
const changeWorkModal = ref(null);
const currentEditId = ref(null);
const router = useRouter();

// 管理员 token，从 sessionStorage 中获取
const token = sessionStorage.getItem('adminToken');

const fetchTemplates = async () => {
  const res = await request.get('/api/admin/template/list', {
    headers: { 'x-access-token': sessionStorage.getItem('adminToken') }
  });
  if (res.data.code === 200) templates.value = res.data.data.list;
};

// 加载作品列表
const fetchWorks = async () => {
  try {
    const { current, pageSize } = pagination.value;
    const params = {
      page: current, size: pageSize,
      ...(filters.value.w_id && { w_id: Number(filters.value.w_id) }),
      ...(filters.value.u_id && { u_id: Number(filters.value.u_id) }),
      ...(filters.value.w_name && { w_name: filters.value.w_name }),
      ...(filters.value.w_description && { w_description: filters.value.w_description }),
      ...(filters.value.t_id && { t_id: filters.value.t_id })
    };
    const res = await request.get('/api/admin/work/list', {
      params, headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      const data = res.data.data;
      // 处理每条记录的 t_name
      works.value.list = await Promise.all(
        data.list.map(async w => ({
          ...w,
          t_name: w.t_id ? await fetchTemplateName(w.t_id) : ''
        }))
      );
      works.value.total = data.total;
      pagination.value.total = data.total;
    } else {
      message.error(res.data.message);
    }
  } catch {
    message.error('获取作品列表失败');
  }
};

const fetchTemplateName = async (t_id) => {
  try {
    const res = await request.get(`/api/template/detail/${t_id}`);
    return res.data.code === 200 ? res.data.data.t_name : '';
  } catch {
    return '';
  }
};

const handleTableChange = ({ current, pageSize }) => {
  pagination.value.current = current;
  pagination.value.pageSize = pageSize;
  fetchWorks();
};
const onSearch = () => { pagination.value.current = 1; fetchWorks(); };
const onReset = () => {
  filters.value = { w_id: '', u_id: '', w_name: '', w_description: '', t_id: null };
  pagination.value.current = 1; fetchWorks();
};

onMounted(() => {
  fetchTemplates();
  fetchWorks();
});

// 跳转至模板详情、作品详情页面
const goToTemplateDetail = (t_id) => {
  router.push(`/templatedetail/${t_id}`);
};

const goToWorkDetail = (w_id) => {
  router.push(`/admin/workdetail/${w_id}`);
};

// 编辑操作：调用编辑模态框并传递当前作品ID
const handleEdit = (record) => {
  currentEditId.value = record.w_id;
  changeWorkModal.value.isVisible = true;
};

// 删除相关变量及操作
const isDeleteWorkModalVisible = ref(false);
const deleteForm = reactive({ verification: '', password: '' });
const currentDeleteWork = ref(null);

const handleDelete = (record) => {
  currentDeleteWork.value = record;
  deleteForm.verification = ''
  deleteForm.password = ''
  isDeleteWorkModalVisible.value = true;
};

const handleDeleteWorkOk = async () => {
  if (!deleteForm.password) {
    message.error('请输入管理员密码')
    return
  }
  if (deleteForm.verification !== `确认删除${currentDeleteWork.value.w_name}`) {
    message.error(`请输入“确认删除${currentDeleteWork.value.w_name}”`)
    return
  }
  try {
    const hashedPwd = CryptoJS.SHA256(deleteForm.password).toString()
    const res = await request.post(
      '/api/admin/work/del',
      { w_id: currentDeleteWork.value.w_id, password: hashedPwd },  // 附带密码
      { headers: { 'x-access-token': token } }
    )
    if (res.data.code === 200 || res.data.code === 201) {
      message.success(res.data.message)
      fetchWorks()
    } else {
      message.error(res.data.message)
    }
  } catch (err) {
    message.error(err.response?.data?.message || '删除作品失败')
  }
  // 重置状态
  isDeleteWorkModalVisible.value = false
  currentDeleteWork.value = null
}

const handleDeleteWorkCancel = () => {
  isDeleteWorkModalVisible.value = false
  currentDeleteWork.value = null
}

const columns = [
  { title: 'ID', dataIndex: 'w_id', key: 'w_id', width: '5%', fixed: 'left' },
  { title: '用户ID', dataIndex: 'u_id', key: 'user_id' },
  { title: '名称', dataIndex: 'w_name', key: 'w_name' },
  { title: '描述', dataIndex: 'w_description', key: 'w_description' },
  { title: '模板', dataIndex: 't_name', key: 't_name' },
  { title: '访问量', dataIndex: 'visit_count', key: 'visit_count' },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time' },
  { title: '更新时间', dataIndex: 'update_time', key: 'update_time' },
  { title: '操作', key: 'action', width: '10%', fixed: 'right' },
];
</script>

<style scoped>
.context_box {
  height: 100vh;
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