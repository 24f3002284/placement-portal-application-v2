<template>
  <div class="card mt-4 ms-4 me-4 mb-4">
    <div class="card-header">
      <div class="d-flex align-items-center">
        <h4 class="mb-0">My Applications</h4>
        <div class="ms-auto d-flex gap-2">
          <button v-if="! is_loading" class="btn btn-outline-primary btn-sm" @click="exportCSV">
            Export CSV
          </button>

          <button v-else class="btn btn-sm btn-primary ms-auto " @click="exportCSV">
            <div class="spinner-border" role="status">
              <span class="visually-hidden">Loading...</span>
            </div>
          </button>
          
        </div>
      </div>
    </div>

    <div v-if="exportMessage" class="alert alert-info mx-3 mt-3 mb-0">{{ exportMessage }}</div>

    <div class="card-body">
      <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
        <li v-for="(status, index) in statuses" :key="status" class="nav-item" role="presentation">
          <button class="nav-link me-1" :class="{ active: index === 0 }"
            :id="`pills-${status}-tab`" data-bs-toggle="pill"
            :data-bs-target="`#pills-${status}`" type="button" role="tab">
            {{ status }}
            <span v-if="applications && applications[status] && applications[status].length > 0"
              class="badge bg-secondary ms-1">{{ applications[status].length }}</span>
          </button>
        </li>
      </ul>

      <div class="tab-content" id="pills-tabContent">
        <div v-for="(status, index) in statuses" :key="status"
          class="tab-pane fade" :class="{ 'show active': index === 0 }"
          :id="`pills-${status}`" role="tabpanel" tabindex="0">

          <table v-if="applications && applications[status] && applications[status].length > 0" class="table table-hover">
            <thead class="table-light">
              <tr>
                <th>Company</th>
                <th>Job Title</th>
                <th>Package</th>
                <th>Applied On</th>
                <th v-if="status === 'Interview'">Interview Details</th>
                <th v-if="status === 'Placed'">Joining Date</th>
                <th>Notes</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="app in applications[status]" :key="app.application_id">
                <td>{{ app['Company Name'] }}</td>
                <td>{{ app['Job Title'] }}</td>
                <td>{{ app['Package'] || 'N/A' }}</td>
                <td>{{ app['Applied At'] }}</td>
                <td v-if="status === 'Interview'">
                  <small>
                    <strong>Date:</strong> {{ app['Interview Date'] || 'TBD' }}<br>
                    <strong>Time:</strong> {{ app['Interview Time'] || 'TBD' }}<br>
                    <strong>Venue:</strong> {{ app['Interview Venue'] || 'TBD' }}
                  </small>
                </td>
                <td v-if="status === 'Placed'">{{ app['Joining Date'] || 'TBD' }}</td>
                <td>{{ app['Notes'] || '–' }}</td>
                <td>
                  <span class="badge" :class="statusBadge(app['Status'])">{{ app['Status'] }}</span>
                </td>
              </tr>
            </tbody>
          </table>
          <div v-else class="text-center text-muted py-4">
            <p>No applications with status: {{ status }}</p>
            <router-link v-if="status === 'Applied'" to="/student/dashboard" class="btn btn-sm btn-outline-primary">
              Browse Drives
            </router-link>
          </div>

        </div>
      </div>
    </div>
  </div>

  <div class="card mt-2 ms-4 me-4 mb-4" v-if="placements && placements.length > 0">
    <div class="card-header"><h5>🎉 My Placements</h5></div>
    <div class="card-body">
      <table class="table table-success table-hover">
        <thead>
          <tr>
            <th>Company</th><th>Position</th><th>Salary</th><th>Joining Date</th><th>Offer Letter</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="p in placements" :key="p.placement_id">
            <td>{{ p['Company Name'] }}</td>
            <td>{{ p['Position'] }}</td>
            <td>{{ p['Salary'] || 'N/A' }}</td>
            <td>{{ p['Joining Date'] || 'TBD' }}</td>
            <td>
              <a v-if="p['Offer Letter URL']" :href="p['Offer Letter URL']" target="_blank"
                class="btn btn-sm btn-outline-success">
                <i class="bi bi-download me-1"></i>Download
              </a>
              <span v-else class="text-muted small">Not uploaded</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentApplications',
  data() {
    return {
      applications: null,
      placements: [],
      exportMessage: null,
      statuses: ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Placed', 'Rejected'],
      task_id:null,
      is_loading:false
    }
  },
  methods: {
    statusBadge(status) {
      const map = {
        'Applied': 'bg-primary', 'Shortlisted': 'bg-info',
        'Interview': 'bg-warning text-dark', 'Offer': 'bg-success',
        'Placed': 'bg-success', 'Rejected': 'bg-danger'
      }
      return map[status] || 'bg-secondary'
    },
    async fetchApplications() {
      try {
        const response = await fetch('http://localhost:5000/api/my-applications', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (response.ok) {
          this.applications = await response.json()
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (e) { this.$router.push('/login') }
    },
    async fetchPlacements() {
      try {
        const response = await fetch('http://localhost:5000/api/my-placements', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (response.ok) {
          this.placements = await response.json()
        }
      } catch (e) { console.error(e) }
    },
    async exportCSV() {
      try {
        this.is_loading = true
        this.exportMessage = null

        const response = await fetch('http://localhost:5000/exportstudentcsv', {
          headers: {
            "Authentication-Token": localStorage.getItem("token"),
            "Content-Type": "application/json"
          }
        })

        if (!response.ok) {
          this.exportMessage = '✗ Export failed. Make sure Redis and Celery are running.'
          this.is_loading = false
          return
        }

        const data = await response.json()
        this.task_id = data.task_id

        const poll_for_csv = setInterval(
          async () => {
            try {
              const res = await fetch(`http://localhost:5000/result/${this.task_id}`, {
                headers: {
                  "Authentication-Token": localStorage.getItem("token"),
                  "Content-Type": "application/json"
                }
              })
              if (res.status == 202) {
                console.log("CSV generation is in progress")
              } else if (res.status == 200) {
                clearInterval(poll_for_csv)
                this.is_loading = false
                window.location.href = `http://localhost:5000/result/${this.task_id}`
              }
            } catch (pollError) {
              clearInterval(poll_for_csv)
              this.is_loading = false
              this.exportMessage = '✗ Export failed. Check server connection.'
            }
          }, 2000
        )
      } catch (error) {
        this.is_loading = false
        this.exportMessage = '✗ Export failed. Check server connection.'
      }
    },
  },
  mounted() {
    this.fetchApplications()
    this.fetchPlacements()
  }
}
</script>