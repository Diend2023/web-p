<template>
  <div class="context_box">
    <!-- 搜索作品 -->
    <a-form layout="inline" class="search-form" :model="filters">
      <a-button type="primary" class="create-work" @click="showCreateWorkModal">创建作品</a-button>
      <a-form-item label="ID">
        <a-input v-model:value="filters.w_id" placeholder="作品ID" style="width:120px" />
      </a-form-item>
      <a-form-item label="名称">
        <a-input v-model:value="filters.w_name" placeholder="作品名称" style="width:180px" />
      </a-form-item>
      <a-form-item label="描述">
        <a-input v-model:value="filters.w_description" placeholder="作品描述" style="width:200px" />
      </a-form-item>
      <a-form-item label="模板">
        <a-select v-model:value="filters.t_id" placeholder="选择模板" style="width:180px" allowClear>
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
    <CreateWork ref="createWorkModal" @created="fetchWorks" />
    <ChangeWork :w_id="currentEditId" ref="changeWorkModal" @updated="fetchWorks" />
    <a-table :columns="columns" :data-source="works" :pagination="pagination" @change="handleTableChange" rowKey="w_id"
      size="middle" :scroll="{ x: 800 }">
      <template #headerCell="{ column }">
        <template v-if="column.key === 'w_name'">
          <span>名称</span>
        </template>
      </template>

      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'w_name'">
          <a @click="goToWorkDetail(record.w_id)">{{ record.w_name }}</a>
        </template>
        <template v-else-if="column.key === 'w_description'">
          <span>{{ record.w_description }}</span>
        </template>
        <template v-else-if="column.key === 't_name'">
          <a @click="goToTemplateDetail(record.t_id)" target="_blank">{{ record.t_name }}</a>
        </template>
        <template v-else-if="column.key === 'action'">
          <span>
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a @click="handleDelete(record)">删除</a>
          </span>
        </template>
      </template>
    </a-table>

    <!-- 删除确认弹窗 -->
    <a-modal v-model:visible="isDeleteWorkModalVisible" title="确认删除作品" @ok="handleDeleteWorkOk"
      @cancel="handleDeleteWorkCancel">
      <a-form>
        <a-form-item label="验证信息" :help="currentDeleteWork ? `请输入“确认删除${currentDeleteWork.w_name}”` : ''">
          <a-input v-model:value="deleteWorkVerification" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import request from '@/utils/request'
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import CreateWork from '@/components/Work/CreateWork.vue';
import ChangeWork from '@/components/Work/ChangeWork.vue';

const works = ref([]);
const templates = ref([]); 
const pagination = ref({
  current: 1, pageSize: 10, total: 0,
  showSizeChanger: true, showQuickJumper: true,
  showTotal: t => `共 ${t} 条`
});
const createWorkModal = ref(null);
const changeWorkModal = ref(null);
const currentEditId = ref(null);
const filters = ref({ w_id: '', w_name: '', w_description: '', t_id: null });
const router = useRouter();

const fetchTemplates = async () => {
  try {
    const token = sessionStorage.getItem('token');
    const res = await request.get('/api/template/list', {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      templates.value = res.data.data.list;
    }
  } catch (e) { console.error(e); }
};

// 拉取列表，带分页和搜索参数
const fetchWorks = async () => {
  try {
    const token = sessionStorage.getItem('token');
    const { current, pageSize } = pagination.value;
    const params = {
      page: current,
      size: pageSize,
      ...(filters.value.w_id && { w_id: Number(filters.value.w_id) }),
      ...(filters.value.w_name && { w_name: filters.value.w_name }),
      ...(filters.value.w_description && { w_description: filters.value.w_description }),
      ...(filters.value.t_id && { t_id: filters.value.t_id })
    };
    const res = await request.get('/api/work/list', {
      params, headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      const { list, total } = res.data.data;
      works.value = await Promise.all(
        list.map(async w => ({
          ...w,
          t_name: w.t_id ? await fetchTemplateName(w.t_id) : null
        }))
      );
      pagination.value.total = total;
    } else {
      message.error(res.data.message);
    }
  } catch {
    message.error('获取列表失败');
  }
};

const fetchTemplateName = async (t_id) => {
  try {
    if (!t_id) {
      return null;
    }
    const response = await request.get(`/api/template/detail/${t_id}`);
    if (response.data.code === 200 || response.data.code === 201) {
      return response.data.data.t_name;
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(
      error.response.data.message
        ? error.response.data.message
        : '未知错误，请联系管理员'
    );
  }
};

const goToTemplateDetail = (t_id) => {
  router.push(`/templatedetail/${t_id}`);
};

const goToWorkDetail = (w_id) => {
  router.push(`/workdetail/${w_id}`);
};

const showCreateWorkModal = () => {
  createWorkModal.value.isVisible = true;
};

// 点击搜索
const onSearch = () => {
  pagination.value.current = 1;
  fetchWorks();
};
// 重置搜索
const onReset = () => {
  filters.value = { w_id:'', w_name:'', w_description:'', t_id: null };
  pagination.value.current = 1;
  fetchWorks();
};

onMounted(() => {
  fetchTemplates();
  fetchWorks();
});

const handleTableChange = ({ current, pageSize }) => {
  pagination.value.current = current;
  pagination.value.pageSize = pageSize;
  fetchWorks();
};

const handleEdit = (record) => {
  currentEditId.value = record.w_id;
  changeWorkModal.value.isVisible = true;
};

// 用于删除确认的相关变量
const isDeleteWorkModalVisible = ref(false);
const deleteWorkVerification = ref('');
const currentDeleteWork = ref(null);

// 点击“删除”按钮时，先弹出确认窗口
const handleDelete = (record) => {
  currentDeleteWork.value = record;
  isDeleteWorkModalVisible.value = true;
};

// 点击确认后，验证用户输入
const handleDeleteWorkOk = async () => {
  if (deleteWorkVerification.value !== `确认删除${currentDeleteWork.value.w_name}`) {
    message.error(`请输入“确认删除${currentDeleteWork.value.w_name}”`);
    return;
  }
  try {
    const token = sessionStorage.getItem('token');
    const response = await request.post(
      '/api/work/del',
      { w_id: currentDeleteWork.value.w_id },
      {
        headers: {
          'x-access-token': token,
        },
      }
    );
    if (response.data.code === 200 || response.data.code === 201) {
      message.success(response.data.message);
      fetchWorks();
    } else {
      message.error(response.data.message);
    }
  } catch (error) {
    message.error(
      error.response?.data?.message ? error.response.data.message : '未知错误，请联系管理员'
    );
  }
  isDeleteWorkModalVisible.value = false;
  deleteWorkVerification.value = '';
  currentDeleteWork.value = null;
};

// 取消删除时清空状态
const handleDeleteWorkCancel = () => {
  isDeleteWorkModalVisible.value = false;
  deleteWorkVerification.value = '';
  currentDeleteWork.value = null;
};

const columns = [
  {
    title: 'ID',
    dataIndex: 'w_id',
    key: 'w_id',
    width: 80,
    fixed: 'left'
  },
  {
    title: '名称',
    dataIndex: 'w_name',
    key: 'w_name',
    width: 200,
    ellipsis: true
  },
  {
    title: '描述',
    dataIndex: 'w_description',
    key: 'w_description',
    ellipsis: true
  },
  {
    title: '模板',
    dataIndex: 't_name',
    key: 't_name',
    width: 150
  },
  {
    title: '操作',
    key: 'action',
    width: 120,
    fixed: 'right'
  }
];
</script>

<style scoped>
.search-form {
  margin-bottom: 16px;
}

.create-work {
  margin-right: 8px;
}

.reset-btn {
  margin-left: 8px;
}

.context_box {
  height: 100vh;
  width: 100%;
  padding: 20px;
}

@media screen and (max-width: 1080px) {}
</style>