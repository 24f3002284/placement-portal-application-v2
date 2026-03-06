<template>
  <router-link to="/company/dashboard" class="btn btn-outline-primary mt-5 ms-5">Go Back</router-link>
  <div class="d-flex justify-content-center mt-4 mb-5">
    <div class="card" style="width: 520px;">
      <div class="card-body">
        <h5 class="mb-3">Create Placement Drive</h5>
        <div v-if="message" class="alert alert-danger">{{ message }}</div>
        <div v-if="success" class="alert alert-success">{{ success }}</div>

        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.job_title" id="floatingTitle" required placeholder="Job Title">
          <label for="floatingTitle">Job Title</label>
        </div>
        <div class="form-floating mb-3">
          <textarea class="form-control" v-model="formdata.job_description" id="floatingDesc" placeholder="Job Description" style="height: 80px"></textarea>
          <label for="floatingDesc">Job Description</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.skills_required" id="floatingSkills" placeholder="Python,React,SQL">
          <label for="floatingSkills">Skills Required (comma-separated)</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.experience_required" id="floatingExp" placeholder="Fresher / 0-2 years">
          <label for="floatingExp">Experience Required</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.package" id="floatingPackage" placeholder="e.g. 8 LPA">
          <label for="floatingPackage">Package (e.g. 8 LPA)</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.benefits" id="floatingBenefits" placeholder="Health insurance, WFH">
          <label for="floatingBenefits">Benefits / Perks</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.location" id="floatingLocation" placeholder="Location">
          <label for="floatingLocation">Job Location</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.eligible_branches" id="floatingBranches" placeholder="CSE,ECE,ME (blank = all)">
          <label for="floatingBranches">Eligible Branches (comma-separated, blank = all)</label>
        </div>
        <div class="form-floating mb-3">
          <input type="number" class="form-control" v-model="formdata.min_cgpa" id="floatingCgpa" placeholder="0.0" step="0.1" min="0" max="10">
          <label for="floatingCgpa">Minimum CGPA</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.eligible_years" id="floatingYears" placeholder="3,4 (blank = all)">
          <label for="floatingYears">Eligible Years e.g. 3,4 (blank = all)</label>
        </div>
        <div class="form-floating mb-3">
          <input type="date" class="form-control" v-model="formdata.application_deadline" id="floatingDeadline" :min="todaysdate()" placeholder="Application Deadline">
          <label for="floatingDeadline">Application Deadline</label>
        </div>
        <div class="form-floating mb-3">
          <input type="date" class="form-control" v-model="formdata.drive_date" id="floatingDriveDate" placeholder="Drive / Interview Date">
          <label for="floatingDriveDate">Drive / Interview Date</label>
        </div>
        <button class="btn btn-primary w-100" @click="createDrive">Create Drive</button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CreateDrive',
  data() {
    return {
      formdata: {
        job_title: '', job_description: '', skills_required: '',
        experience_required: '', package: '', benefits: '',
        location: '', eligible_branches: '', min_cgpa: 0,
        eligible_years: '', application_deadline: '', drive_date: ''
      },
      message: null,
      success: null
    }
  },
  methods: {
    todaysdate() {
      const today = new Date()
      const y = today.getFullYear()
      const m = String(today.getMonth() + 1).padStart(2, '0')
      const d = String(today.getDate()).padStart(2, '0')
      return `${y}-${m}-${d}`
    },
    async createDrive() {
      try {
        const response = await fetch('http://localhost:5000/api/create-drive', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authentication-Token': localStorage.getItem('token') },
          body: JSON.stringify(this.formdata)
        })
        const data = await response.json()
        if (response.status === 201) {
          this.success = data.message
          setTimeout(() => this.$router.push('/company/dashboard'), 1500)
        } else if (response.status === 401) {
          this.$router.push('/login')
        } else if (response.status === 403) {
          this.message = data.message || 'Your company is not approved yet'
        } else {
          this.message = data.message || 'An error occurred'
        }
      } catch (error) {
        this.message = 'An error occurred while creating the drive.'
      }
    }
  }
}
</script>
