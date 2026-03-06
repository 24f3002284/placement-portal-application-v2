<template>
  <div class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="card" style="width: 480px;">
      <div class="card-body p-4">
        <h5 class="card-title text-center mb-3">Student Registration</h5>
        <div class="alert alert-danger" v-if="message">{{ message }}</div>
        <div class="alert alert-success" v-if="success">{{ success }}</div>

        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.name" id="floatingName" placeholder="Full Name" required>
          <label for="floatingName">Full Name</label>
        </div>
        <div class="form-floating mb-3">
          <input type="email" class="form-control" v-model="formdata.email" id="floatingEmail" placeholder="name@example.com" required>
          <label for="floatingEmail">Email address</label>
        </div>
        <div class="form-floating mb-3">
          <input type="password" class="form-control" v-model="formdata.password" id="floatingPassword" placeholder="Password" required>
          <label for="floatingPassword">Password</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.roll_number" id="floatingRoll" placeholder="Roll Number">
          <label for="floatingRoll">Roll Number</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.branch" id="floatingBranch" placeholder="Branch">
          <label for="floatingBranch">Branch (e.g. CSE, ECE)</label>
        </div>
        <div class="form-floating mb-3">
          <input type="number" class="form-control" v-model="formdata.cgpa" id="floatingCgpa" placeholder="CGPA" step="0.01" min="0" max="10">
          <label for="floatingCgpa">CGPA (out of 10)</label>
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
          <input type="text" class="form-control" v-model="formdata.skills" id="floatingSkills" placeholder="Python,Java,SQL">
          <label for="floatingSkills">Skills (comma-separated)</label>
        </div>
        <div class="form-floating mb-3">
          <textarea class="form-control" v-model="formdata.experience" id="floatingExp" placeholder="Experience" style="height:80px"></textarea>
          <label for="floatingExp">Experience / Internships</label>
        </div>
        <button class="btn btn-primary w-100" @click="register">Register</button>
        <div class="text-center mt-3">
          <router-link to="/login" class="small">Already have an account? Login</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'StudentRegisterComp',
  data() {
    return {
      formdata: {
        name: '', email: '', password: '', roll_number: '',
        branch: '', cgpa: '', year: '', mobile: '', skills: '', experience: ''
      },
      message: '',
      success: ''
    }
  },
  methods: {
    async register() {
      try {
        const response = await fetch('http://localhost:5000/register?role=student', {
          method: 'POST',
          body: JSON.stringify(this.formdata),
          headers: { 'Content-Type': 'application/json' }
        })
        const data = await response.json()
        if (response.status === 201) {
          this.success = data.message
          setTimeout(() => this.$router.push('/login'), 2000)
        } else {
          this.message = data.message
        }
      } catch (e) {
        this.message = 'Cannot connect to server'
      }
    }
  }
}
</script>
