<template>
  <div class="d-flex justify-content-center align-items-center" style="min-height: 100vh;">
    <div class="card" style="width: 480px;">
      <div class="card-body p-4">
        <h5 class="card-title text-center mb-3">Company Registration</h5>
        <div class="alert alert-danger" v-if="message">{{ message }}</div>
        <div class="alert alert-success" v-if="success">{{ success }}</div>

        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.name" id="floatingName" placeholder="Company Name" required>
          <label for="floatingName">Company Name</label>
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
          <input type="text" class="form-control" v-model="formdata.hr_contact" id="floatingHR" placeholder="HR Contact Name">
          <label for="floatingHR">HR Contact Name</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.industry" id="floatingIndustry" placeholder="e.g. IT, Finance">
          <label for="floatingIndustry">Industry</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.location" id="floatingLocation" placeholder="e.g. Bangalore">
          <label for="floatingLocation">Headquarters Location</label>
        </div>
        <div class="form-floating mb-3">
          <input type="text" class="form-control" v-model="formdata.website" id="floatingWebsite" placeholder="https://company.com">
          <label for="floatingWebsite">Website URL</label>
        </div>
        <div class="form-floating mb-3">
          <textarea class="form-control" v-model="formdata.description" id="floatingDesc" placeholder="Company Description" style="height: 80px"></textarea>
          <label for="floatingDesc">Company Description</label>
        </div>
        <button class="btn btn-success w-100" @click="register">Register Company</button>
        <p class="text-muted small text-center mt-2">Requires admin approval before dashboard access</p>
        <div class="text-center">
          <router-link to="/login" class="small">Already registered? Login</router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CompanyRegisterComp',
  data() {
    return {
      formdata: {
        name: '', email: '', password: '', hr_contact: '',
        industry: '', location: '', website: '', description: ''
      },
      message: '',
      success: ''
    }
  },
  methods: {
    async register() {
      try {
        const response = await fetch('http://localhost:5000/register?role=company', {
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
