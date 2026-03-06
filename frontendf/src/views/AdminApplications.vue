<template>
  <div class="card mt-4 ms-4 me-4 mb-4">
    <div class="card-header d-flex align-items-center">
      <h4 class="mb-0">All Student Applications</h4>
      <span class="ms-3 badge bg-secondary">{{ allApplications.length }} total</span>
    </div>
    <div class="card-body">

      <!-- Filter bar -->
      <div class="row mb-3 g-2">
        <div class="col-md-4">
          <input class="form-control" v-model="filterStudent" placeholder="Filter by student name...">
        </div>
        <div class="col-md-4">
          <input class="form-control" v-model="filterCompany" placeholder="Filter by company name...">
        </div>
        <div class="col-md-4">
          <select class="form-select" v-model="filterStatus">
            <option value="">All Statuses</option>
            <option v-for="s in statuses" :key="s" :value="s">{{ s }}</option>
          </select>
        </div>
      </div>

      <table class="table table-hover" v-if="filtered.length">
        <thead class="table-light">
          <tr>
            <th>#</th>
            <th>Student</th>
            <th>Branch / CGPA</th>
            <th>Company</th>
            <th>Job Title</th>
            <th>Package</th>
            <th>Applied On</th>
            <th>Interview Date</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(a, i) in filtered" :key="a.application_id">
            <td>{{ i + 1 }}</td>
            <td>
              {{ a['Student Name'] }}<br>
              <small class="text-muted">{{ a['Student Email'] }}</small>
            </td>
            <td>{{ a['Branch'] }} | {{ a['CGPA'] }}</td>
            <td>{{ a['Company Name'] }}</td>
            <td>{{ a['Job Title'] }}</td>
            <td>{{ a['Package'] || '–' }}</td>
            <td>{{ a['Applied At'] }}</td>
            <td>{{ a['Interview Date'] || '–' }}</td>
            <td>
              <span class="badge" :class="statusBadge(a['Status'])">{{ a['Status'] }}</span>
            </td>
          </tr>
        </tbody>
      </table>

      <p v-else class="text-muted text-center py-4">No applications found.</p>

    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminApplications',
  data() {
    return {
      allApplications: [],
      filterStudent: '',
      filterCompany: '',
      filterStatus: '',
      statuses: ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Placed', 'Rejected']
    }
  },
  computed: {
    filtered() {
      return this.allApplications.filter(a => {
        return (
          (!this.filterStudent || a['Student Name'].toLowerCase().includes(this.filterStudent.toLowerCase())) &&
          (!this.filterCompany || a['Company Name'].toLowerCase().includes(this.filterCompany.toLowerCase())) &&
          (!this.filterStatus || a['Status'] === this.filterStatus)
        )
      })
    }
  },
  methods: {
    statusBadge(status) {
      const map = {
        'Applied': 'bg-primary', 'Shortlisted': 'bg-info text-dark',
        'Interview': 'bg-warning text-dark', 'Offer': 'bg-success',
        'Placed': 'bg-success', 'Rejected': 'bg-danger'
      }
      return map[status] || 'bg-secondary'
    },
    async fetchApplications() {
      try {
        const res = await fetch('http://localhost:5000/api/all-applications', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (res.ok) {
          this.allApplications = await res.json()
        } else if (res.status === 401) {
          this.$router.push('/login')
        }
      } catch (e) { console.error(e) }
    }
  },
  mounted() { this.fetchApplications() }
}
</script>