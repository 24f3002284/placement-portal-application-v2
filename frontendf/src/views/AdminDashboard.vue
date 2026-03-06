<template>
  <div class="container-fluid mt-3">

    <!-- Stats Row -->
    <div v-if="stats" class="row g-3 ms-2 me-2 mb-4">
      <div class="col-md-2">
        <div class="card border-start border-primary border-4 p-3">
          <div class="text-muted small">Students</div>
          <div class="fs-3 fw-bold">{{ stats.total_students }}</div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card border-start border-success border-4 p-3">
          <div class="text-muted small">Companies</div>
          <div class="fs-3 fw-bold">{{ stats.total_companies }}</div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card border-start border-info border-4 p-3">
          <div class="text-muted small">Drives</div>
          <div class="fs-3 fw-bold">{{ stats.total_drives }}</div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card border-start border-secondary border-4 p-3">
          <div class="text-muted small">Applications</div>
          <div class="fs-3 fw-bold">{{ stats.total_applications }}</div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card border-start border-success border-4 p-3">
          <div class="text-muted small">Placed</div>
          <div class="fs-3 fw-bold text-success">{{ stats.total_placements }}</div>
        </div>
      </div>
      <div class="col-md-2">
        <div class="card border-start border-warning border-4 p-3">
          <div class="text-muted small">Pending Approvals</div>
          <div class="fs-3 fw-bold text-warning">{{ stats.pending_companies + stats.pending_drives }}</div>
        </div>
      </div>
    </div>

    <!-- Companies -->
    <div v-if="companies" class="ms-3 me-3 mt-3">
      <UsersCard :users="companies" usertype="company" />
    </div>

    <!-- Students -->
    <div v-if="students" class="ms-3 me-3 mt-3 mb-4">
      <UsersCard :users="students" usertype="student" />
    </div>

  </div>
</template>

<script>
import UsersCard from '../components/UsersCard.vue'

export default {
  name: 'AdminDashboard',
  components: { UsersCard },
  data() {
    return {
      companies: null,
      students: null,
      stats: null
    }
  },
  methods: {
    async fetchStats() {
      try {
        const response = await fetch('http://localhost:5000/api/admin-stats', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (response.ok) {
          this.stats = await response.json()
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (err) { console.log(err) }
    },
    async fetchCompanies() {
      try {
        const response = await fetch('http://localhost:5000/api/companies', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        const data = await response.json()
        if (response.ok) {
          this.companies = data
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (err) { console.log(err) }
    },
    async fetchStudents() {
      try {
        const response = await fetch('http://localhost:5000/api/students', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        const data = await response.json()
        if (response.ok) {
          this.students = data
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (err) { console.log(err) }
    }
  },
  mounted() {
    this.fetchStats()
    this.fetchCompanies()
    this.fetchStudents()
  }
}
</script>
