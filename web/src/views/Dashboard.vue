<template>
  <div class="all">
    <div class="list">
      <a-button class="list_btn" type="primary" style="margin-bottom: 16px" @click="toggleCollapsed">
        <MenuUnfoldOutlined v-if="state.collapsed" />
        <MenuFoldOutlined v-else />
      </a-button>
      <a-menu v-model:openKeys="state.openKeys" v-model:selectedKeys="state.selectedKeys" mode="inline"
        theme="light" :inline-collapsed="state.collapsed" :items="items"></a-menu>
    </div>
    <div class="content">
      <keep-alive>
        <component :is="currentComponent" @goWork="handleGoWork" />
      </keep-alive>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { reactive, computed, watch, h } from 'vue';
import {
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  PieChartOutlined,
  UserOutlined,
  InboxOutlined,
} from '@ant-design/icons-vue';

// 定义内容组件
import ContentOne from '@/components/DashboardMain.vue';
import ContentTwo from '@/components/User.vue';
import ContentThree from '@/components/Work.vue';

// 尝试从 sessionStorage 中恢复选中的菜单，默认 ['1']
const savedSelectedKeys = sessionStorage.getItem('dashboardSelectedKeys');
const state = reactive({
  collapsed: false,
  selectedKeys: savedSelectedKeys ? JSON.parse(savedSelectedKeys) : ['1'],
  openKeys: ['sub1'],
  preOpenKeys: ['sub1'],
});

const items = reactive([
  {
    key: '1',
    icon: () => h(PieChartOutlined),
    label: '控制台',
  },
  {
    key: '2',
    icon: () => h(UserOutlined),
    label: '用户中心',
  },
  {
    key: '3',
    icon: () => h(InboxOutlined),
    label: '作品中心',
  },
]);

const componentsMap = {
  '1': ContentOne,
  '2': ContentTwo,
  '3': ContentThree
};

const currentComponent = computed(() => {
  return componentsMap[state.selectedKeys[0]] || ContentOne;
});

const handleGoWork = () => {
  state.selectedKeys = ['3'];
};

// 监听选中菜单变化，将状态保存到 sessionStorage
watch(() => state.selectedKeys, (newVal) => {
  sessionStorage.setItem('dashboardSelectedKeys', JSON.stringify(newVal));
}, { deep: true });

const toggleCollapsed = () => {
  let list = document.querySelector('.list') as HTMLElement;
  let list_ul = document.querySelector('.list ul') as HTMLElement;
  state.collapsed = !state.collapsed;
  state.openKeys = state.collapsed ? [] : state.preOpenKeys;
  if (list.style.width == '50px') {
    list_ul.style.width = '100%';
    list.style.width = '256px';
  } else {
    list_ul.style.width = '50px';
    list.style.width = '50px';
  }
};
</script>

<style scoped>
.all {
  display: flex;
  height: 100%;
}

.list {
  padding-top: 0px;
  border-top: 1px solid #cccccc;
  width: 256px;
}

.list ul {
  height: 100dvh;
}

.list_btn {
  display: none;
}

.content {
  padding-top: 0px;
  border-top: 1px solid #cccccc;
  width: 100%;
}

@media screen and (max-width: 1080px) {
  .list {
    margin-top: 75px;
  }

  .content {
    margin-top: 75px;
  }
}

@media screen and (max-width: 768px) {
  .list_btn {
    display: block;
  }

  .content {
    margin-left: 0;
  }
}
</style>