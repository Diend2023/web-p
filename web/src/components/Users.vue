<template>
  <div class="context_box">
    <a-form layout="inline" class="search-form" :model="filters">
      <a-form-item label="ID">
        <a-input v-model:value="filters.u_id" placeholder="用户id" style="width:100px" />
      </a-form-item>
      <a-form-item label="UID">
        <a-input v-model:value="filters.user_id" placeholder="用户UID" style="width:140px" />
      </a-form-item>
      <a-form-item label="用户名">
        <a-input v-model:value="filters.username" placeholder="用户名" style="width:140px" />
      </a-form-item>
      <a-form-item label="邮箱">
        <a-input v-model:value="filters.email" placeholder="用户邮箱" style="width:180px" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="onSearch">搜索</a-button>
        <a-button class="reset-btn" @click="onReset">重置</a-button>
      </a-form-item>
    </a-form>

    <a-table :columns="columns" :data-source="users.list" :pagination="pagination" @change="handleTableChange"
      rowKey="u_id" size="middle" :scroll="{ x: 800 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex && record[column.dataIndex] !== undefined">
          <span>{{ record[column.dataIndex] }}</span>
        </template>
        <!-- 操作列 -->
        <template v-else-if="column.key === 'action'">
          <span>
            <a @click="handleEdit(record)">编辑</a>
            <a-divider type="vertical" />
            <a @click="handleDelete(record)">删除</a>
          </span>
        </template>
      </template>
    </a-table>

    <a-modal v-model:visible="isEditUserModalVisible" title="编辑用户" @ok="handleEditUserOk"
      @cancel="handleEditUserCancel">
      <a-form :model="editForm">
        <a-form-item label="用户名" name="username" :rules="[{ required: false }]">
          <a-input v-model:value="editForm.username" placeholder="输入用户名" />
        </a-form-item>
        <a-form-item label="邮箱" name="email" :rules="[{ required: false, type: 'email' }]">
          <a-input v-model:value="editForm.email" placeholder="输入邮箱" />
        </a-form-item>
        <a-form-item label="管理员密码" name="password" :rules="[{ required: true, message: '请输入管理员密码' }]">
          <a-input-password type="password" v-model:value="editForm.password" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal v-model:visible="isDeleteUserModalVisible" title="确认删除用户" @ok="handleDeleteUserOk"
      @cancel="handleDeleteUserCancel" >
      <a-form :model="deleteForm">
        <a-form-item label="验证信息" name="verification"  :help="currentDeleteUser ? `请输入“确认删除${currentDeleteUser.username}”` : ''"
          :rules="[{ required: true }]">
          <a-input v-model:value="deleteForm.verification" />
        </a-form-item>
        <a-form-item label="管理员密码" name="password" :rules="[{ required: true, message: '请输入管理员密码' }]">
          <a-input-password type="password" v-model:value="deleteForm.password" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive } from 'vue';
import request from '@/utils/request'
import { message } from 'ant-design-vue';
import CryptoJS from 'crypto-js';

// 用户列表
const users = ref([]);
const filters = ref({ u_id: '', user_id: '', username: '', email: '' });
const pagination = ref({
  current: 1, pageSize: 10, total: 0,
  showSizeChanger: true, showQuickJumper: true,
  showTotal: t => `共 ${t} 条`
});

// 管理员 token
const token = sessionStorage.getItem('adminToken')

// 获取用户列表
const fetchUsers = async () => {
  try {
    const { current, pageSize } = pagination.value;
    const params = {
      page: current, size: pageSize,
      ...(filters.value.u_id && { u_id: Number(filters.value.u_id) }),
      ...(filters.value.user_id && { user_id: filters.value.user_id }),
      ...(filters.value.username && { username: filters.value.username }),
      ...(filters.value.email && { email: filters.value.email })
    };
    const res = await request.get('/api/admin/user/list', {
      params, headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      users.value = res.data.data;
      pagination.value.total = res.data.data.total;
    } else {
      message.error(res.data.message);
    }
  } catch {
    message.error('获取用户列表失败');
  }
};

const handleTableChange = ({ current, pageSize }) => {
  pagination.value.current = current;
  pagination.value.pageSize = pageSize;
  fetchUsers();
};
const onSearch = () => { pagination.value.current = 1; fetchUsers(); };
const onReset = () => {
  filters.value = { u_id: '', user_id: '', username: '', email: '' };
  pagination.value.current = 1; fetchUsers();
};

onMounted(() => {
  fetchUsers();
});

// 表格列配置
const columns = [
  { title: 'ID', dataIndex: 'u_id', key: 'u_id', width: '5%', fixed: 'left' },
  { title: 'UID', dataIndex: 'user_id', key: 'user_id' },
  { title: '用户名', dataIndex: 'username', key: 'username' },
  { title: '邮箱', dataIndex: 'email', key: '', width: '20%' },
  { title: '注册时间', dataIndex: 'create_time', key: 'create_time' },
  { title: '更新时间', dataIndex: 'update_time', key: 'update_time' },
  { title: '最后登录时间', dataIndex: 'last_login_time', key: 'last_login_time' },
  { title: '操作', key: 'action', width: '10%', fixed: 'right' }
];

// 编辑动作：打开编辑弹窗并预填数据
const editForm = reactive({ username: '', email: '', password: '' });
const isEditUserModalVisible = ref(false);
const currentEditUser = ref(null);

const handleEdit = (record) => {
  currentEditUser.value = record;
  editForm.username = record.username;
  editForm.email = record.email;
  editForm.password = '';
  isEditUserModalVisible.value = true;
};

const handleEditUserOk = async () => {
  if (!editForm.password) {
    message.error('请输入管理员密码进行验证');
    return;
  }
  try {
    const encryptedPassword = CryptoJS.SHA256(editForm.password).toString();
    const res = await request.post(
      '/api/admin/user/set',
      {
        u_id: currentEditUser.value.u_id,
        username: editForm.username,
        email: editForm.email,
        password: encryptedPassword
      },
      { headers: { 'x-access-token': token } }
    );
    if (res.data.code === 200) {
      message.success(res.data.message);
      fetchUsers();
    } else {
      message.error(res.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '编辑用户失败');
  }
  isEditUserModalVisible.value = false;
  currentEditUser.value = null;
};

// 取消编辑
const handleEditUserCancel = () => {
  isEditUserModalVisible.value = false;
  currentEditUser.value = null;
};

// 删除相关变量及操作
const deleteForm = reactive({ verification: '', password: '' })
const isDeleteUserModalVisible = ref(false)
const currentDeleteUser = ref(null)

const handleDelete = record => {
  currentDeleteUser.value = record
  deleteForm.verification = ''
  deleteForm.password = ''
  isDeleteUserModalVisible.value = true
}

async function handleDeleteUserOk() {
  if (deleteForm.verification !== `确认删除${currentDeleteUser.value.username}`) {
    return message.error(`请输入“确认删除${currentDeleteUser.value.username}”`)
  }
  if (!deleteForm.password) {
    return message.error('请输入管理员密码')
  }
  try {
    const hashed = CryptoJS.SHA256(deleteForm.password).toString()
    const res = await request.post(
      '/api/admin/user/del',
      { u_id: currentDeleteUser.value.u_id, password: hashed },
      { headers: { 'x-access-token': token } }
    )
    if (res.data.code === 200) {
      message.success(res.data.message)
      fetchUsers()
    } else {
      message.error(res.data.message)
    }
  } catch (err) {
    message.error(err.response?.data?.message || '删除用户失败')
  }
  isDeleteUserModalVisible.value = false
  currentDeleteUser.value = null
}

function handleDeleteUserCancel() {
  isDeleteUserModalVisible.value = false
  currentDeleteUser.value = null
}
</script>

<style scoped>
.context_box {
  min-height: 100vh;
  width: 100%;
  padding: 20px;
  background: #f5f5f5;
}

.search-form {
  margin-bottom: 16px;
}

.reset-btn {
  margin-left: 8px;
}

.context_box {
  padding: 20px;
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