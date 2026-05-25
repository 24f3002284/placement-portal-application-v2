<template>
  <div class="card mt-4 ms-4 me-4 mb-4">
    <div class="card-header"><h4>Admin Search</h4></div>
    <div class="card-body">

      <div class="mb-3">
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" v-model="query_type" value="student" id="radioStudent">
          <label class="form-check-label" for="radioStudent">Search Students</label>
        </div>
        <div class="form-check form-check-inline">
          <input class="form-check-input" type="radio" v-model="query_type" value="company" id="radioCompany">
          <label class="form-check-label" for="radioCompany">Search Companies</label>
        </div>
      </div>

      <div class="d-flex gap-2 mb-4">
        <div class="form-floating flex-grow-1">
          <input type="text" class="form-control" v-model="query" id="floatingSearch"
            :placeholder="query_type === 'student' ? 'Name, email, or roll number...' : 'Name, email, or industry...'"
            @keyup.enter="search">
          <label for="floatingSearch">
            {{ query_type === 'student' ? 'Search by name / email / roll number' : 'Search by name / email / industry' }}
          </label>
        </div>
        <button class="btn btn-primary px-4" @click="search">Search</button>
      </div>

      <!-- Student Results -->
      <div v-if="query_type === 'student' && results && results.length">
        <h5>Student Results ({{ results.length }})</h5>
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th>Name</th><th>Email</th><th>Roll No.</th>
              <th>Branch</th><th>CGPA</th><th>Year</th><th>Skills</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in results" :key="s.student_id">
              <td>{{ s['Student Name'] }}</td>
              <td>{{ s['Student Email'] }}</td>
              <td>{{ s['Roll Number'] || '–' }}</td>
              <td>{{ s['Branch'] }}</td>
              <td>{{ s['CGPA'] }}</td>
              <td>{{ s['Year'] }}</td>
              <td><small>{{ s['Skills'] || '–' }}</small></td>
              <td>
                <span class="badge" :class="s['Status'] === 'Active' ? 'bg-success' : 'bg-danger'">
                  {{ s['Status'] }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Company Results -->
      <div v-if="query_type === 'company' && results && results.length">
        <h5>Company Results ({{ results.length }})</h5>
        <table class="table table-hover">
          <thead class="table-light">
            <tr>
              <th>Name</th><th>Email</th><th>HR Contact</th>
              <th>Industry</th><th>Location</th><th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in results" :key="c.company_id">
              <td>{{ c['Company Name'] }}</td>
              <td>{{ c['Company Email'] }}</td>
              <td>{{ c['HR Contact'] || '–' }}</td>
              <td>{{ c['Industry'] || '–' }}</td>
              <td>{{ c['Location'] || '–' }}</td>
              <td>
                <span class="badge" :class="statusBadge(c['Status'])">{{ c['Status'] }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <p v-if="searched && results && results.length === 0" class="text-muted text-center py-3">
        No results found for "{{ query }}"
      </p>

    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminSearch',
  data() {
    return {
      query_type: 'student',
      query: '',
      results: null,
      searched: false
    }
  },
  methods: {
    statusBadge(status) {
      const map = {
        'Approved': 'bg-success', 'Registered': 'bg-warning text-dark',
        'Rejected': 'bg-danger', 'Blacklisted': 'bg-dark', 'Active': 'bg-success'
      }
      return map[status] || 'bg-secondary'
    },
    async search() {
      if (!this.query.trim()) return
      this.searched = false
      try {
        const response = await fetch(
          `${import.meta.env.VITE_API_URL}/api/admin-search?query_type=${this.query_type}&query=${encodeURIComponent(this.query)}`,
          { headers: { 'Authentication-Token': localStorage.getItem('token') } }
        )
        if (response.ok) {
          this.results = await response.json()
          this.searched = true
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (err) { console.error(err) }
    }
  }
}
</script>
