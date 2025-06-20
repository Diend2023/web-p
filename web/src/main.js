import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Antd from 'ant-design-vue';
import 'ant-design-vue/dist/reset.css';
import VueCodemirror from 'vue-codemirror-next'


const app = createApp(App);

app.use(router);

app.use(Antd);

app.use(VueCodemirror)

app.mount('#app');

