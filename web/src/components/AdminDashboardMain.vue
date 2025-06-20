<template>
  <div class="context_box">
    <a-row gutter="16">
      <!-- 总作品数 -->
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <FileOutlined class="card-icon" />
              <span>总作品数</span>
            </div>
          </template>
          <p class="card-value">{{ worksCount }}</p>
        </a-card>
      </a-col>
      <!-- 总作品访问量 -->
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <EyeOutlined class="card-icon" />
              <span>总作品访问量</span>
            </div>
          </template>
          <p class="card-value">{{ worksTotalVisits }}</p>
        </a-card>
      </a-col>
      <!-- 平均作品访问量 -->
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <BarChartOutlined class="card-icon" />
              <span>平均作品访问量</span>
            </div>
          </template>
          <p class="card-value">{{ worksAverageVisits }}</p>
        </a-card>
      </a-col>
    </a-row>

    <a-row gutter="16" class="second-row">
      <!-- 总用户数 -->
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <UserOutlined class="card-icon" />
              <span>总用户数</span>
            </div>
          </template>
          <p class="card-value">{{ usersCount }}</p>
        </a-card>
      </a-col>
      <!-- 总管理员数 -->
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <TeamOutlined class="card-icon" />
              <span>总管理员数</span>
            </div>
          </template>
          <p class="card-value">{{ adminsCount }}</p>
        </a-card>
      </a-col>
      <!-- 总模板数 -->
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <AppstoreOutlined class="card-icon" />
              <span>总模板数</span>
            </div>
          </template>
          <p class="card-value">{{ templatesCount }}</p>
        </a-card>
      </a-col>
    </a-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import request from '@/utils/request'
import { message } from 'ant-design-vue';
// 导入图标组件
import { FileOutlined, EyeOutlined, BarChartOutlined, UserOutlined, TeamOutlined, AppstoreOutlined } from '@ant-design/icons-vue';

// 作品、用户、管理员、模板数据（API返回的数据格式为 { list: [...], total: X }）
const works = ref({});
const users = ref({});
const admins = ref({});
const templates = ref({});

// 更新后的计算属性，如果 total 属性存在，则显示 total，否则取数组长度
const worksCount = computed(() =>
  works.value.total !== undefined ? works.value.total : (Array.isArray(works.value) ? works.value.length : 0)
);
const worksTotalVisits = computed(() =>
  works.value.list ? works.value.list.reduce((sum, work) => sum + (Number(work.visit_count) || 0), 0) : 0
);
const worksAverageVisits = computed(() =>
  worksCount.value ? (worksTotalVisits.value / worksCount.value).toFixed(2) : 0
);

const usersCount = computed(() =>
  users.value.total !== undefined ? users.value.total : (Array.isArray(users.value) ? users.value.length : 0)
);
const adminsCount = computed(() =>
  admins.value.total !== undefined ? admins.value.total : (Array.isArray(admins.value) ? admins.value.length : 0)
);
const templatesCount = computed(() =>
  templates.value.total !== undefined ? templates.value.total : (Array.isArray(templates.value) ? templates.value.length : 0)
);

// 后端接口调用（需要管理员 token）
const token = sessionStorage.getItem('adminToken');

const fetchWorks = async () => {
  try {
    const res = await request.get('/api/admin/work/list', {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      works.value = res.data.data; // data 是 { list: [...], total: ... }
    } else {
      message.error(res.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '获取作品列表失败');
  }
};

const fetchUsers = async () => {
  try {
    const res = await request.get('/api/admin/user/list', {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      users.value = res.data.data;
    } else {
      message.error(res.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '获取用户列表失败');
  }
};

const fetchAdmins = async () => {
  try {
    const res = await request.get('/api/admin/admin/list', {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      admins.value = res.data.data;
    } else {
      message.error(res.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '获取管理员列表失败');
  }
};

const fetchTemplates = async () => {
  try {
    const res = await request.get('/api/admin/template/list', {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      templates.value = res.data.data;
    } else {
      message.error(res.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '获取模板列表失败');
  }
};

onMounted(() => {
  fetchWorks();
  fetchUsers();
  fetchAdmins();
  fetchTemplates();
});
</script>

<style scoped>
.context_box {
  min-height: 100vh;
  width: 100%;
  padding: 20px;
  background: #f5f5f5;
}

.custom-card {
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  margin-bottom: 16px;
}

.card-title {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: 600;
}

.card-icon {
  font-size: 24px;
  color: #1890ff;
  margin-right: 8px;
}

.card-value {
  font-size: 32px;
  font-weight: bold;
  text-align: center;
  margin: 0;
  color: #1890ff;
}

/* 针对 1080px 屏幕 */
@media screen and (max-width: 1080px) {
  .context_box {
    padding: 20px;
  }

  .card-title {
    font-size: 16px;
  }

  .card-icon {
    font-size: 20px;
    margin-right: 6px;
  }

  .card-value {
    font-size: 28px;
  }
}

/* 针对 768px 屏幕 - 卡片竖向排列 */
@media screen and (max-width: 768px) {
  .context_box {
    padding: 10px;
  }

  .ant-row {
    flex-direction: column;
  }

  .ant-row>.ant-col {
    width: 100% !important;
    max-width: 100% !important;
    margin-bottom: 16px;
  }
}
</style>