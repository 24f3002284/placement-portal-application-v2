<template>
  <Navbar v-if="showNavbar" />
  <router-view />
</template>

<script>
import Navbar from './components/Navbar.vue'

export default {
  name: 'App',
  components: { Navbar },
  computed: {
    showNavbar() {
      const noNavRoutes = ['/login', '/student/register', '/company/register', '/']
      return !noNavRoutes.includes(this.$route.path)
    }
  }
}
</script>
