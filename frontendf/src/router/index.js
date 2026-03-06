import { createRouter, createWebHistory } from 'vue-router'
import Home from '../views/Home.vue'
import Login from '../views/Login.vue'
import StudentRegister from '../views/StudentRegister.vue'
import CompanyRegister from '../views/CompanyRegister.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import AdminSearch from '../views/AdminSearch.vue'
import AdminDrives from '../views/AdminDrives.vue'
import AdminApplications from '../views/AdminApplications.vue'
import CompanyDashboard from '../views/CompanyDashboard.vue'
import CreateDrive from '../views/CreateDrive.vue'
import DriveApplications from '../views/DriveApplications.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import StudentApplications from '../views/StudentApplications.vue'
import StudentProfile from '../views/StudentProfile.vue'

const routes = [
  { path: '/', component: Home },
  { path: '/login', component: Login },
  { path: '/student/register', component: StudentRegister },
  { path: '/company/register', component: CompanyRegister },
  { path: '/admin/dashboard', component: AdminDashboard },
  { path: '/admin/search', component: AdminSearch },
  { path: '/admin/drives', component: AdminDrives },
  { path: '/admin/applications', component: AdminApplications },
  { path: '/company/dashboard', component: CompanyDashboard },
  { path: '/company/create-drive', component: CreateDrive },
  { path: '/company/drive-applications/:id', component: DriveApplications },
  { path: '/student/dashboard', component: StudentDashboard },
  { path: '/student/applications', component: StudentApplications },
  { path: '/student/profile', component: StudentProfile },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router