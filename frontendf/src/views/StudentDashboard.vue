<template>
  <div class="card mt-4 ms-4 me-4">
    <div class="card-header">
      <div class="d-flex align-items-center">
        <h4 class="mb-0">Available Placement Drives</h4>
        <div class="ms-auto">
          <input class="form-control" v-model="searchQuery" @input="fetchDrives"
            placeholder="Search by title, skills, location..." style="width: 280px;">
        </div>
      </div>
    </div>
    <div class="card-body">
      <div class="alert alert-info alert-dismissible" v-if="message">
        {{ message }}
        <button type="button" class="btn-close" @click="message=null"></button>
      </div>

      <div v-if="drives && drives.length > 0" class="row">
        <div v-for="drive in drives" :key="drive.drive_id" class="col-md-4 mb-4">
          <div class="card h-100" :class="drive.eligible ? 'border-primary' : 'border-secondary'">
            <div class="card-header d-flex align-items-center">
              <div>
                <strong>{{ drive['Job Title'] }}</strong><br>
                <small class="text-primary">{{ drive['Company Name'] }}</small>
              </div>
              <span class="ms-auto badge" :class="drive.eligible ? 'bg-success' : 'bg-secondary'">
                {{ drive.eligible ? 'Eligible' : 'Not Eligible' }}
              </span>
            </div>
            <div class="card-body small">
              <p class="mb-1"><i class="bi bi-cash me-1"></i><strong>{{ drive['Package'] || 'N/A' }}</strong></p>
              <p class="mb-1"><i class="bi bi-geo-alt me-1"></i>{{ drive['Location'] || 'N/A' }}</p>
              <p class="mb-1"><i class="bi bi-tools me-1"></i>{{ drive['Skills Required'] || 'Any' }}</p>
              <p class="mb-1"><i class="bi bi-briefcase me-1"></i>{{ drive['Experience Required'] || 'Fresher' }}</p>
              <p class="mb-1"><i class="bi bi-diagram-3 me-1"></i>Branches: {{ drive['Eligible Branches'] || 'All' }}</p>
              <p class="mb-1"><i class="bi bi-star me-1"></i>Min CGPA: {{ drive['Min CGPA'] }}</p>
              <p class="mb-1"><i class="bi bi-calendar me-1"></i>Deadline: {{ drive['Application Deadline'] || 'Open' }}</p>
              <p class="mb-1"><i class="bi bi-calendar-event me-1"></i>Drive Date: {{ drive['Drive Date'] || 'TBD' }}</p>
              <p class="mb-1 text-muted">{{ drive['Industry'] }}</p>
            </div>
            <div class="card-footer">
              <span v-if="drive.applied" class="badge bg-success w-100 p-2">✓ Applied</span>
              <button v-else-if="drive.eligible" class="btn btn-primary btn-sm w-100"
                @click="applyDrive(drive.drive_id)">Apply Now</button>
              <button v-else class="btn btn-secondary btn-sm w-100" disabled>Not Eligible</button>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-muted text-center mt-4">No approved drives available right now.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentDashboard',
  data() {
    return {
      drives: [],
      searchQuery: '',
      message: null
    }
  },
  methods: {
    async fetchDrives() {
      try {
        const q = encodeURIComponent(this.searchQuery)
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/get-drives?q=${q}`, {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (response.ok) {
          this.drives = await response.json()
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (error) { console.error(error) }
    },
    async applyDrive(drive_id) {
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/apply-drive/${drive_id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') }
        })
        const data = await response.json()
        if (response.status === 201) {
          this.message = '✓ ' + data.message
          this.fetchDrives()
        } else if (response.status === 401) {
          this.$router.push('/login')
        } else {
          this.message = data.message
        }
      } catch (error) { this.message = 'An error occurred while applying.' }
    }
  },
  mounted() { this.fetchDrives() }
}
</script>
