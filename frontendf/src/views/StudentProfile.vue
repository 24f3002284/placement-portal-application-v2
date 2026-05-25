<template>
  <router-link to="/student/dashboard" class="btn btn-outline-primary mt-5 ms-5">Go Back</router-link>
  <div class="d-flex justify-content-center mt-4 mb-5">
    <div class="card" style="width: 500px;">
      <div class="card-body">
        <h5 class="mb-3">My Profile</h5>
        <div v-if="message" class="alert alert-danger">{{ message }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.branch" id="floatingBranch" placeholder="Branch">
          <label for="floatingBranch">Branch (e.g. CSE)</label>
        </div>
        <div class="form-floating mb-3">
          <input type="number" class="form-control" v-model="formdata.cgpa" id="floatingCgpa" placeholder="CGPA" step="0.01" min="0" max="10">
          <label for="floatingCgpa">CGPA</label>
        </div>
        <div class="form-floating mb-3">
          <input type="number" class="form-control" v-model="formdata.year" id="floatingYear" placeholder="Year" min="1" max="4">
          <label for="floatingYear">Current Year (1–4)</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.mobile" id="floatingMobile" placeholder="Mobile">
          <label for="floatingMobile">Phone Number</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.skills" id="floatingSkills" placeholder="Python,React,SQL">
          <label for="floatingSkills">Skills (comma-separated)</label>
        </div>
        <div class="form-floating mb-3">
          <textarea class="form-control" v-model="formdata.experience" id="floatingExp" placeholder="Experience" style="height:80px">
          </textarea>
          <label for="floatingExp">Experience / Internships</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.resume_url" id="floatingResume" placeholder="Resume URL">
          <label for="floatingResume">Resume URL (Google Drive / LinkedIn)</label>
        </div>
        <button class="btn btn-primary w-100" @click="updateProfile">Update Profile</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentProfile',
  data() {
    return {
      formdata: { branch: '', cgpa: '', year: '', mobile: '', skills: '', experience: '', resume_url: '' },
      message: null,
      success: null
    }
  },
  methods: {
    async fetchProfile() {
      try {
        const response = await fetch('${import.meta.env.VITE_API_URL}/api/student-profile', {
          headers: { 'Authentication-Token': localStorage.getItem('token') }
        })
        if (response.ok) {
          const data = await response.json()
          this.formdata = {
            branch: data.branch || '', cgpa: data.cgpa || '',
            year: data.year || '', mobile: data.mobile || '',
            skills: data.skills || '', experience: data.experience || '',
            resume_url: data.resume_url || ''
          }
        } else if (response.status === 401) {
          this.$router.push('/login')
        }
      } catch (error) { console.error(error) }
    },
    async updateProfile() {
      try {
        const response = await fetch('${import.meta.env.VITE_API_URL}/api/update-student-profile', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') },
          body: JSON.stringify(this.formdata)
        })
        const data = await response.json()
        if (response.ok) {
          this.success = data.message
        } else if (response.status === 401) {
          this.$router.push('/login')
        } else {
          this.message = data.message || 'Error updating profile'
        }
      } catch (error) {
        this.message = 'An error occurred'
      }
    }
  },
  mounted() { this.fetchProfile() }
}
</script>
