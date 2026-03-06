<template>
  <div class="container mt-5">
    <div class="text-center">
      <h1><i class="bi bi-mortarboard-fill"></i> Placement Portal</h1>
      <p class="text-muted">Campus Recruitment Management System</p>
      <div class="mt-4">
        <router-link to="/login" class="btn btn-primary mx-2">Login</router-link>
        <router-link to="/student/register" class="btn btn-secondary mx-2">Student Register</router-link>
        <router-link to="/company/register" class="btn btn-success mx-2">Company Register</router-link>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeComp'
}
</script>
