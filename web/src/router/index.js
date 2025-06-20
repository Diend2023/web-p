import { createRouter, createWebHashHistory } from 'vue-router';
import Home from '@/views/Home.vue';
import RegisterOrlogin from '@/views/RegisterOrlogin.vue';
import Logout from '@/views/Logout.vue';
import Templates from '@/views/Templates.vue';
import TemplateDetail from '@/views/TemplateDetail.vue';
import WorkDetail from '@/views/WorkDetail.vue';
import Dashboard from '@/views/Dashboard.vue';
import Admin from '@/views/Admin.vue';
import AdminLogin from '@/views/AdminLogin.vue';
import AdminDashboard from '@/views/AdminDashboard.vue';
import AdminWorkDetail from '@/views/AdminWorkDetail.vue';
import AdminLogout from '@/views/AdminLogout.vue';
import TemplatePreview from '@/views/TemplatePreview.vue'
import WorkPreview from '@/views/WorkPreview.vue'


const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/registerorlogin', name: 'RegisterOrlogin', component: RegisterOrlogin },
  { path: '/dashboard', name: 'Dashboard', component: Dashboard, meta: { requiresAuth: true } },
  { path: '/logout', name: 'Logout', component: Logout },
  { path: '/templates', name: 'Templates', component: Templates},
  { path: '/templatedetail/:id', name: 'TemplateDetail', component: TemplateDetail, props: true},
  { path: '/templatepreview/:id', name: 'TemplatePreview', component: TemplatePreview, props: true },
  { path: '/workdetail/:id', name: 'WorkDetail', component: WorkDetail, props: true, meta: { requiresAuth: true }},
  { path: '/admin', name: 'Admin', meta: { admin: true }, component: Admin},
  { path: '/workpreview/:userId/:id', name: 'WorkPreview', component: WorkPreview, props: true },
  { path: '/admin/login', name: 'AdminLogin', component: AdminLogin , meta: { admin: true }},
  { path: '/admin/logout', name: 'AdminLogout', component: AdminLogout, meta: { admin: true }},
  { path: '/admin/dashboard', name: 'AdminDashboard', component: AdminDashboard, meta: { admin: true, requiresAuth: true }},
  { path: '/admin/workdetail/:id', name: 'AdminWorkDetail', component: AdminWorkDetail, props: true, meta: { admin: true, requiresAuth: true }},
];

const router = createRouter({  
  history: createWebHashHistory(),  
  routes  
})

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否是管理员页面
    if (to.matched.some(record => record.meta.admin)) {
      const adminToken = sessionStorage.getItem('adminToken');
      if (!adminToken) {
        next({ name: 'AdminLogin' });
        return;
      }
    } else {
      // 普通用户页面
      const token = sessionStorage.getItem('token');
      if (!token) {
        next({ name: 'RegisterOrlogin' });
        return;
      }
    }
    next();
  } else {
    next();
  }
});
export default router;
