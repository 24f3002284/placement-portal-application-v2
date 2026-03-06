<template>
  <nav class="navbar navbar-expand-lg bg-body-tertiary">
    <div class="container-fluid">
      <a class="navbar-brand fw-bold" href="#"><i class="bi bi-mortarboard-fill me-2"></i>Placement Portal</a>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto me-5">

          <!-- Admin Nav -->
          <template v-if="role === 'admin'">
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/admin/dashboard' }" to="/admin/dashboard">
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/admin/drives' }" to="/admin/drives">
                Drives
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/admin/applications' }" to="/admin/applications">
                Applications
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/admin/search' }" to="/admin/search">
                Search
              </router-link>
            </li>
          </template>

          <!-- Company Nav -->
          <template v-if="role === 'company'">
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/company/dashboard' }" to="/company/dashboard">
                Dashboard
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/company/create-drive">
                Create Drive
              </router-link>
            </li>
          </template>

          <!-- Student Nav -->
          <template v-if="role === 'student'">
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/student/dashboard' }" to="/student/dashboard">
                Drives
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/student/applications' }" to="/student/applications">
                My Applications
              </router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :class="{ active: $route.path === '/student/profile' }" to="/student/profile">
                Profile
              </router-link>
            </li>
          </template>

          <!-- User dropdown -->
          <li class="nav-item">
            <div class="dropdown">
              <button class="btn dropdown-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false">
                <i class="bi bi-person-circle fs-4 ms-2"></i>
              </button>
              <ul class="dropdown-menu dropdown-menu-end">
                <li><span class="dropdown-item-text text-muted small">{{ email }}</span></li>
                <li><hr class="dropdown-divider"></li>
                <li><button class="dropdown-item" @click="logout">Logout</button></li>
              </ul>
            </div>
          </li>

        </ul>
      </div>
    </div>
  </nav>
</template>

<script>
export default ({
  name: 'NavbarComp',
  data() {
    return {
      role: localStorage.getItem('role'),
      email: localStorage.getItem('email')
    }
  },
  methods: {
    logout() {
      localStorage.removeItem('token')
      localStorage.removeItem('role')
      localStorage.removeItem('email')
      this.$router.push('/login')
    }
  }
})
</script>