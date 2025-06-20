<template>
    <div>
        <a-float-button shape="circle" type="primary" :style="{
            right: '24px',
        }" @click="toggleChatbox">
            <template #icon>
                <CustomerServiceOutlined />
            </template>
        </a-float-button>
        <div v-if="chatboxVisible" class="chatbox-container">
            <iframe
                src="https://copilotstudio.microsoft.com/environments/Default-8ffbc1c4-4886-4de9-a22f-531e7533c0d0/bots/Default_YqB-OY7R1IRayzsoOBiMl/webchat?__version__=2"
                frameborder="0" style="width: 100%; height: 100%;"></iframe>
        </div>
    </div>
</template>

<script lang="ts" setup>
import { ref } from 'vue';
import { CustomerServiceOutlined } from '@ant-design/icons-vue';

const chatboxVisible = ref(false);

const toggleChatbox = () => {
    chatboxVisible.value = !chatboxVisible.value;
};
</script>

<style scoped>
.chatbox-container {
    position: fixed;
    bottom: 60px;
    right: 20px;
    width: 300px;
    height: 400px;
    border: 1px solid #ddd;
    border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    background-color: #fff;
    z-index: 1000;
    margin-bottom: 30px;
}

.chatbox-container iframe {
    width: 100%;
    height: calc(100% - 30px);
    border: none;
}
</style>