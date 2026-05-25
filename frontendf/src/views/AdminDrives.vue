<template>
  <div class="ms-5 me-5 mt-3">
    <div class="card">
      <div class="card-header">
        <h3>Placement Drives</h3>
      </div>
      <div class="card-body">
        <ul class="nav nav-pills mb-3" id="pills-tab" role="tablist">
          <li v-for="(status, index) in statuses" :key="status" class="nav-item me-3" role="presentation">
            <button class="nav-link" :class="{ active: index === 0 }" :id="`pills-${status}-tab`"
              data-bs-toggle="pill" :data-bs-target="`#pills-${status}`"
              type="button" role="tab">
              {{ status }}
            </button>
          </li>
        </ul>

        <div class="tab-content" id="pills-tabContent">
          <div v-for="(status, index) in statuses" :key="status" class="tab-pane fade"
            :class="{ 'show active': index === 0 }" :id="`pills-${status}`" role="tabpanel" tabindex="0">

            <div v-if="drives && drives[status] && drives[status].length > 0">
              <table class="table">
                <thead>
                  <tr>
                    <th>Company</th>
                    <th>Job Title</th>
                    <th>Package</th>
                    <th>Location</th>
                    <th>Min CGPA</th>
                    <th>Branches</th>
                    <th>Deadline</th>
                    <th>Applicants</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(drive, i) in drives[status]" :key="i">
                    <td>{{ drive['Company Name'] }}</td>
                    <td>{{ drive['Job Title'] }}</td>
                    <td>{{ drive['Package'] }}</td>
                    <td>{{ drive['Location'] }}</td>
                    <td>{{ drive['Min CGPA'] }}</td>
                    <td>{{ drive['Eligible Branches'] || 'All' }}</td>
                    <td>{{ drive['Application Deadline'] || 'Open' }}</td>
                    <td>{{ drive['Applicant Count'] }}</td>
                    <td>
                      <button v-if="drive['Status'] === 'Pending'" class="btn btn-success btn-sm me-1"
                        @click="approveDrive(drive['drive_id'])">Approve</button>
                      <button v-if="drive['Status'] === 'Pending'" class="btn btn-danger btn-sm"
                        @click="rejectDrive(drive['drive_id'])">Reject</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div v-else>
              <p class="text-muted">No drives with status: {{ status }}</p>
            </div>

          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AdminDrives',
  data() {
    return {
      drives: null,
      statuses: ['Pending', 'Approved', 'Rejected', 'Closed']
    }
  },
  methods: {
    async fetchDrives() {
      try {
        const response = await fetch('${import.meta.env.VITE_API_URL}/api/all-drives', {
          method: 'GET',
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        const data = await response.json()
        if (response.ok) {
          this.drives = data
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (err) {
        console.log(err)
      }
    },
    async approveDrive(drive_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/approve-drive/${drive_id}`, {
        method: 'GET',
        headers: { 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else {
        alert(data.message || 'Error approving drive')
      }
    },
    async rejectDrive(drive_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/reject-drive/${drive_id}`, {
        method: 'GET',
        headers: { 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else {
        alert(data.message || 'Error rejecting drive')
      }
    }
  },
  mounted() {
    this.fetchDrives()
  }
}
</script>
