<template>
  <div v-if="perticular_users && perticular_users.users && perticular_users.users.length > 0">

    <!-- Company Table -->
    <table v-if="usertype === 'company'" class="table">
      <thead>
        <tr>
          <th scope="col">Company Name</th>
          <th scope="col">Email</th>
          <th scope="col">HR Contact</th>
          <th scope="col">Website</th>
          <th scope="col">Status</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, index) in perticular_users.users" :key="index">
          <td>{{ user['Company Name'] }}</td>
          <td>{{ user['Company Email'] }}</td>
          <td>{{ user['HR Contact'] }}</td>
          <td>
            <a v-if="user['Website']" :href="user['Website']" target="_blank" class="small">{{ user['Website'] }}</a>
            <span v-else>-</span>
          </td>
          <td>{{ user['Status'] }}</td>
          <td>
            <button v-if="user['Status'] === 'Registered'" class="btn btn-success btn-sm me-2"
              @click="approveCompany(user['company_id'])">Approve</button>
            <button v-if="user['Status'] === 'Registered'" class="btn btn-danger btn-sm me-2"
              @click="rejectCompany(user['company_id'])">Reject</button>
            <button v-if="user['Status'] === 'Approved'" class="btn btn-warning btn-sm me-2"
              @click="blacklistCompany(user['company_id'])">Blacklist</button>
            <button v-if="user['Status'] === 'Blacklisted'" class="btn btn-secondary btn-sm me-2"
              @click="unblacklistCompany(user['company_id'])">Unblacklist</button>
          </td>
        </tr>
      </tbody>
    </table>

    <!-- Student Table -->
    <table v-if="usertype === 'student'" class="table">
      <thead>
        <tr>
          <th scope="col">Name</th>
          <th scope="col">Email</th>
          <th scope="col">Branch</th>
          <th scope="col">CGPA</th>
          <th scope="col">Year</th>
          <th scope="col">Mobile</th>
          <th scope="col">Status</th>
          <th scope="col">Actions</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(user, index) in perticular_users.users" :key="index">
          <td>{{ user['Student Name'] }}</td>
          <td>{{ user['Student Email'] }}</td>
          <td>{{ user['Branch'] }}</td>
          <td>{{ user['CGPA'] }}</td>
          <td>{{ user['Year'] }}</td>
          <td>{{ user['Mobile'] }}</td>
          <td>{{ user['Status'] }}</td>
          <td>
            <button v-if="user['Status'] === 'Active'" class="btn btn-warning btn-sm"
              @click="blacklistStudent(user['student_id'])">Blacklist</button>
            <button v-if="user['Status'] === 'Blacklisted'" class="btn btn-secondary btn-sm"
              @click="unblacklistStudent(user['student_id'])">Unblacklist</button>
          </td>
        </tr>
      </tbody>
    </table>

  </div>
  <div v-else>
    <p class="text-muted">No {{ usertype }}s found for status: {{ perticular_users.status }}</p>
  </div>
</template>

<script>
export default ({
  name: 'UsersTable',
  props: {
    perticular_users: { type: Object, required: true },
    usertype: { type: String, required: true }
  },
  methods: {
    async approveCompany(company_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/approve-company/${company_id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else if (response.status === 401) {
        alert('Session expired. Please log in again.')
        this.$router.push('/login')
      } else if (response.status === 403) {
        this.$router.push('/login')
      } else {
        alert(data.message || 'An error occurred')
      }
    },
    async rejectCompany(company_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/reject-company/${company_id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else if (response.status === 401) {
        alert('Session expired. Please log in again.')
        this.$router.push('/login')
      } else {
        alert(data.message || 'An error occurred')
      }
    },
    async blacklistCompany(company_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/blacklist-company/${company_id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else {
        alert(data.message || 'An error occurred')
      }
    },
    async unblacklistCompany(company_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/unblacklist-company/${company_id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else {
        alert(data.message || 'An error occurred')
      }
    },
    async blacklistStudent(student_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/blacklist-student/${student_id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else if (response.status === 401) {
        alert('Session expired. Please log in again.')
        this.$router.push('/login')
      } else {
        alert(data.message || 'An error occurred')
      }
    },
    async unblacklistStudent(student_id) {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/api/unblacklist-student/${student_id}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') }
      })
      const data = await response.json()
      if (response.ok) {
        this.$router.go(0)
      } else if (response.status === 401) {
        alert('Session expired. Please log in again.')
        this.$router.push('/login')
      } else {
        alert(data.message || 'An error occurred')
      }
    }
  }
})
</script>
