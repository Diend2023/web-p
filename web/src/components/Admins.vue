<template>
  <div class="context_box">
    <a-form layout="inline" class="search-form" :model="filters">
      <!-- 添加创建管理员按钮 -->
      <a-button type="primary" class="create-admin" @click="showCreateAdminModal">
        创建管理员
      </a-button>
      <a-form-item label="ID">
        <a-input v-model:value="filters.a_id" placeholder="管理员id" style="width:100px" />
      </a-form-item>
      <a-form-item label="AID">
        <a-input v-model:value="filters.admin_id" placeholder="管理员AID" style="width:100px" />
      </a-form-item>
      <a-form-item label="管理员名">
        <a-input v-model:value="filters.adminname" placeholder="管理员名" style="width:140px" />
      </a-form-item>
      <a-form-item label="邮箱">
        <a-input v-model:value="filters.email" placeholder="管理员邮箱" style="width:180px" />
      </a-form-item>
      <a-form-item>
        <a-button type="primary" @click="onSearch">搜索</a-button>
        <a-button class="reset-btn" @click="onReset">重置</a-button>
      </a-form-item>
    </a-form>

    <!-- 添加创建管理员弹窗 -->
    <CreateAdmin ref="createAdminModal" @created="fetchAdmins" />

    <a-table :columns="columns" :data-source="admins.list" :pagination="pagination" @change="handleTableChange"
      rowKey="a_id" size="middle" :scroll="{ x: 1000 }">
      <template #bodyCell="{ column, record }">
        <template v-if="column.dataIndex && record[column.dataIndex] !== undefined">
          <span>{{ record[column.dataIndex] }}</span>
        </template>
        <template v-else-if="column.key === 'action'">
          <span></span>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import request from '@/utils/request'
import { message } from 'ant-design-vue'
import CreateAdmin from '@/components/Admin/CreateAdmin.vue'

const admins = ref({ list: [], total: 0 })
const filters = ref({
  a_id: '',
  admin_id: '',
  adminname: '',
  email: ''
})
const pagination = ref({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: t => `共 ${t} 条`
})

const token = sessionStorage.getItem('adminToken')

// 获取管理员列表
const fetchAdmins = async () => {
  try {
    const { current, pageSize } = pagination.value
    const params = {
      page: current,
      size: pageSize,
      ...(filters.value.a_id && { a_id: Number(filters.value.a_id) }),
      ...(filters.value.admin_id && { admin_id: filters.value.admin_id }),
      ...(filters.value.adminname && { adminname: filters.value.adminname }),
      ...(filters.value.email && { email: filters.value.email })
    }
    const res = await request.get('/api/admin/admin/list', {
      params,
      headers: { 'x-access-token': token }
    })
    if (res.data.code === 200) {
      admins.value.list = res.data.data.list
      pagination.value.total = res.data.data.total
    } else {
      message.error(res.data.message)
    }
  } catch {
    message.error('获取管理员列表失败')
  }
}

const handleTableChange = ({ current, pageSize }) => {
  pagination.value.current = current
  pagination.value.pageSize = pageSize
  fetchAdmins()
}
const onSearch = () => {
  pagination.value.current = 1
  fetchAdmins()
}
const onReset = () => {
  filters.value = { a_id: '', admin_id: '', adminname: '', email: '' }
  pagination.value.current = 1
  fetchAdmins()
}

onMounted(fetchAdmins)

const columns = [
  { title: 'ID', dataIndex: 'a_id', key: 'a_id', width: '5%', fixed: 'left' },
  { title: 'AID', dataIndex: 'admin_id', key: 'admin_id' },
  { title: '管理员名', dataIndex: 'adminname', key: 'adminname' },
  { title: '邮箱', dataIndex: 'email', key: 'email' },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time' },
  { title: '更新时间', dataIndex: 'update_time', key: 'update_time' },
  { title: '操作', key: 'action', width: '10%', fixed: 'right' }
]

const createAdminModal = ref(null)
const showCreateAdminModal = () => {
  createAdminModal.value.isVisible = true
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

.create-admin {
  margin-right: 8px;
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