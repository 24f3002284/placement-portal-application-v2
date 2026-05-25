<template>
  <div class="alert alert-info alert-dismissible mt-3 ms-4 me-4" v-if="message">
    {{ message }}
    <button type="button" class="btn-close" @click="message=null"></button>
  </div>

  <!-- Company Profile -->
  <div class="card mt-3 ms-4 me-4" v-if="profile">
    <div class="card-header d-flex align-items-center">
      <div>
        <h5 class="mb-0">{{ profile.name }}</h5>
        <small class="text-muted">{{ profile.industry }} | {{ profile.location }}</small>
      </div>
      <span class="ms-auto badge fs-6" :class="profile.status === 'Approved' ? 'bg-success' : 'bg-warning text-dark'">
        {{ profile.status }}
      </span>
    </div>
    <div class="card-body row small">
      <div class="col-md-3"><strong>HR:</strong> {{ profile.hr_contact || 'N/A' }}</div>
      <div class="col-md-3"><strong>Website:</strong>
        <a v-if="profile.website" :href="profile.website" target="_blank">{{ profile.website }}</a>
        <span v-else>N/A</span>
      </div>
      <div class="col-md-6"><strong>About:</strong> {{ profile.description || 'N/A' }}</div>
    </div>
  </div>

  <!-- Drives Card -->
  <div class="card mt-4 ms-4 me-4 mb-4">
    <div class="card-header">
      <div class="d-flex align-items-center">
        <h4 class="mb-0">My Placement Drives</h4>
        <div class="ms-auto d-flex gap-2">
          <button class="btn btn-outline-secondary btn-sm" @click="exportCSV">
            <i class="bi bi-download me-1"></i>Export CSV
          </button>
          <button class="btn btn-outline-danger btn-sm" @click="exportPDF">
            <i class="bi bi-file-earmark-pdf me-1"></i>Export PDF
          </button>
          <router-link to="/company/create-drive" class="btn btn-primary btn-sm">
            <i class="bi bi-plus-circle me-1"></i>Create Drive
          </router-link>
        </div>
      </div>
    </div>

    <div v-if="exportMessage" class="alert alert-info mx-3 mt-3 mb-0">{{ exportMessage }}</div>

    <div class="card-body">
      <div v-if="drives && drives.length > 0" class="row">
        <div v-for="drive in drives" :key="drive.drive_id" class="col-md-4 mb-3">
          <div class="card h-100">
            <div class="card-header d-flex align-items-center">
              <strong>{{ drive.job_title }}</strong>
              <span class="ms-auto badge" :class="statusBadge(drive.status)">{{ drive.status }}</span>
            </div>
            <div class="card-body small">
              <p class="mb-1"><i class="bi bi-cash me-1"></i>{{ drive.package || 'N/A' }}</p>
              <p class="mb-1"><i class="bi bi-geo-alt me-1"></i>{{ drive.location || 'N/A' }}</p>
              <p class="mb-1"><i class="bi bi-tools me-1"></i>{{ drive.skills_required || 'Any' }}</p>
              <p class="mb-1"><i class="bi bi-briefcase me-1"></i>{{ drive.experience_required || 'Fresher' }}</p>
              <p class="mb-1"><i class="bi bi-gift me-1"></i>{{ drive.benefits || 'N/A' }}</p>
              <p class="mb-1"><i class="bi bi-diagram-3 me-1"></i>{{ drive.eligible_branches || 'All' }}</p>
              <p class="mb-1"><i class="bi bi-star me-1"></i>Min CGPA: {{ drive.min_cgpa }}</p>
              <p class="mb-1"><i class="bi bi-calendar me-1"></i>Deadline: {{ drive.application_deadline || 'Open' }}</p>
              <p class="mb-1"><i class="bi bi-people me-1"></i>{{ drive.applicant_count }} applicant(s)</p>
            </div>
            <div class="card-footer d-flex gap-2">
              <router-link v-if="drive.status === 'Approved'" :to="`/company/drive-applications/${drive.drive_id}`"
                class="btn btn-outline-primary btn-sm flex-grow-1">View Applications</router-link>
              <button v-if="drive.status === 'Approved'" class="btn btn-outline-danger btn-sm"
                @click="closeDrive(drive.drive_id)" title="Close Drive">
                <i class="bi bi-x-circle"></i>
              </button>
            </div>
          </div>
        </div>
      </div>
      <p v-else class="text-muted text-center py-4">No drives created yet.
        <router-link to="/company/create-drive">Create one now</router-link>
      </p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyDashboard',
  data() {
    return {
      drives: null,
      profile: null,
      message: null,
      exportMessage: null
    }
  },
  methods: {
    statusBadge(status) {
      return {
        'bg-success': status === 'Approved',
        'bg-warning text-dark': status === 'Pending',
        'bg-danger': status === 'Rejected',
        'bg-secondary': status === 'Closed'
      }
    },
    async fetchProfile() {
      try {
        const response = await fetch('${import.meta.env.VITE_API_URL}/api/company-profile', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (response.ok) {
          this.profile = await response.json()
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (e) { console.error(e) }
    },
    async fetchDrives() {
      try {
        const response = await fetch('${import.meta.env.VITE_API_URL}/api/get-drives', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (response.ok) {
          this.drives = await response.json()
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (e) { console.error(e) }
    },
    async closeDrive(drive_id) {
      if (!confirm('Are you sure you want to close this drive? Students will no longer be able to apply.')) return
      try {
        const response = await fetch(`${import.meta.env.VITE_API_URL}/api/close-drive/${drive_id}`, {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        const data = await response.json()
        if (response.ok) {
          this.message = data.message
          this.fetchDrives()
        } else {
          this.message = data.message
        }
      } catch (e) { console.error(e) }
    },
    async exportCSV() {
      this.exportMessage = 'Preparing download...'
      try {
        const response = await fetch('${import.meta.env.VITE_API_URL}/exportcompanycsv', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (!response.ok) {
          this.exportMessage = '✗ Export failed. Make sure Redis and Celery are running.'
          return
        }
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'company_applications.csv'
        a.click()
        window.URL.revokeObjectURL(url)
        this.exportMessage = null
      } catch (e) {
        this.exportMessage = '✗ Export failed. Check server connection.'
      }
    },
    async exportPDF() {
      this.exportMessage = 'Generating PDF...'
      try {
        const response = await fetch('${import.meta.env.VITE_API_URL}/exportcompanypdf', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (!response.ok) {
          this.exportMessage = '✗ PDF export failed. Make sure Redis and Celery are running.'
          return
        }
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'company_report.pdf'
        a.click()
        window.URL.revokeObjectURL(url)
        this.exportMessage = null
      } catch (e) {
        this.exportMessage = '✗ PDF export failed. Check server connection.'
      }
    }
  },
  mounted() {
    this.fetchProfile()
    this.fetchDrives()
  }
}
</script>