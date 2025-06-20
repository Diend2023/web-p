<template>
  <div class="context_box">
    <a-row gutter="16">
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <FileOutlined class="card-icon" />
              <span>我的作品数量</span>
            </div>
          </template>
          <template #extra>
            <a @click="goToWork">查看详情</a>
          </template>
          <p class="card-value">{{ worksCount }}</p>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <EyeOutlined class="card-icon" />
              <span>总作品访问量</span>
            </div>
          </template>
          <p class="card-value">{{ totalVisits }}</p>
        </a-card>
      </a-col>
      <a-col :span="8">
        <a-card class="custom-card" style="width: 100%">
          <template #title>
            <div class="card-title">
              <BarChartOutlined class="card-icon" />
              <span>平均作品访问量</span>
            </div>
          </template>
          <p class="card-value">{{ averageVisits }}</p>
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
import { FileOutlined, EyeOutlined, BarChartOutlined } from '@ant-design/icons-vue';

const works = ref({ list: [], total: 0 });    // <-- 由 [] 改为 { list, total }

// 作品数量
const worksCount = computed(() => works.value.total);
// 总访问量
const totalVisits = computed(() =>
  works.value.list.reduce((sum, work) => sum + (Number(work.visit_count) || 0), 0)
);
// 平均访问量
const averageVisits = computed(() =>
  worksCount.value ? (totalVisits.value / worksCount.value).toFixed(2) : 0
);

const fetchWorks = async () => {
  try {
    const token = sessionStorage.getItem('token');
    const res = await request.get('/api/work/list', {
      headers: { 'x-access-token': token }
    });
    if (res.data.code === 200) {
      works.value.list = res.data.data.list;
      works.value.total = res.data.data.total;
    } else {
      message.error(res.data.message);
    }
  } catch (error) {
    message.error(error.response?.data?.message || '获取作品列表失败');
  }
};

onMounted(() => {
  fetchWorks();
});

// 点击查看更多时，触发事件传递给父组件
const goToWork = () => {
  // 通过事件让父组件切换到作品中心
  emit('goWork');
};

const emit = defineEmits(['goWork']);
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

@media screen and (max-width: 768px) {
  .context_box {
    padding: 10px;
  }
  .ant-row {
    flex-direction: column;
  }
  .ant-row > .ant-col {
    width: 100% !important;
    max-width: 100% !important;
    margin-bottom: 16px;
  }
  .custom-card {
    margin-bottom: 16px;
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
</style>