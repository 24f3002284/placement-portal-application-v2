<template>
  <router-link to="/company/dashboard" class="btn btn-outline-primary mt-4 ms-4">← Back</router-link>

  <div class="card mt-3 ms-4 me-4 mb-4">
    <div class="card-header"><h5>Drive Applications</h5></div>
    <div class="card-body">

      <div v-if="message" class="alert alert-info alert-dismissible">
        {{ message }} <button class="btn-close" @click="message=null"></button>
      </div>

      <ul class="nav nav-pills mb-3">
        <li v-for="(s, i) in statuses" :key="s" class="nav-item">
          <button class="nav-link me-1" :class="{active: i===0}"
            :id="`tab-${s}`" data-bs-toggle="pill" :data-bs-target="`#pane-${s}`" type="button">
            {{ s }}
            <span v-if="applications[s] && applications[s].length" class="badge bg-secondary ms-1">{{ applications[s].length }}</span>
          </button>
        </li>
      </ul>

      <div class="tab-content">
        <div v-for="(s, i) in statuses" :key="s" class="tab-pane fade" :class="{show:i===0, active:i===0}" :id="`pane-${s}`">

          <div v-if="applications[s] && applications[s].length">
            <div v-for="app in applications[s]" :key="app.application_id" class="card mb-3">
              <div class="card-body">
                <div class="row">
                  <div class="col-md-4">
                    <strong>{{ app['Student Name'] }}</strong><br>
                    <small>{{ app['Student Email'] }}</small><br>
                    <small>{{ app['Branch'] }} | CGPA: {{ app['CGPA'] }} | Yr {{ app['Year'] }}</small><br>
                    <small class="text-muted">Skills: {{ app['Skills'] || '–' }}</small><br>
                    <small class="text-muted">Exp: {{ app['Experience'] || '–' }}</small><br>
                    <a v-if="app['Resume URL']" :href="app['Resume URL']" target="_blank" class="btn btn-sm btn-outline-secondary mt-1">Resume</a>
                  </div>
                  <div class="col-md-4">
                    <small><strong>Applied:</strong> {{ app['Applied At'] }}</small><br>
                    <small v-if="app['Interview Date']"><strong>Interview:</strong> {{ app['Interview Date'] }} {{ app['Interview Time'] }}<br>{{ app['Interview Venue'] }}</small>
                    <small v-if="app['Notes']"><br><strong>Notes:</strong> {{ app['Notes'] }}</small>
                  </div>
                  <div class="col-md-4">
                    <!-- Action buttons depending on current status -->
                    <div class="d-flex flex-column gap-2">
                      <template v-if="s === 'Applied'">
                        <button class="btn btn-primary btn-sm" @click="setStatus(app.application_id, 'Shortlisted')">Shortlist</button>
                        <button class="btn btn-danger btn-sm" @click="setStatus(app.application_id, 'Rejected')">Reject</button>
                      </template>
                      <template v-if="s === 'Shortlisted'">
                        <div class="input-group input-group-sm mb-1">
                          <input type="date" class="form-control" v-model="app._iDate" placeholder="Interview date">
                        </div>
                        <input type="text" class="form-control form-control-sm mb-1" v-model="app._iTime" placeholder="Time e.g. 10:00 AM">
                        <input type="text" class="form-control form-control-sm mb-1" v-model="app._iVenue" placeholder="Venue / Zoom link">
                        <button class="btn btn-warning btn-sm text-dark" @click="scheduleInterview(app)">Schedule Interview</button>
                        <button class="btn btn-danger btn-sm" @click="setStatus(app.application_id, 'Rejected')">Reject</button>
                      </template>
                      <template v-if="s === 'Interview'">
                        <button class="btn btn-success btn-sm" @click="setStatus(app.application_id, 'Offer')">Send Offer</button>
                        <button class="btn btn-danger btn-sm" @click="setStatus(app.application_id, 'Rejected')">Reject</button>
                      </template>
                      <template v-if="s === 'Offer'">
                        <input type="date" class="form-control form-control-sm mb-1" v-model="app._joiningDate" placeholder="Joining date">
                        <input type="text" class="form-control form-control-sm mb-1" v-model="app._offerUrl" placeholder="Offer letter URL">
                        <button class="btn btn-success btn-sm" @click="markPlaced(app)">Confirm Placed</button>
                      </template>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <p v-else class="text-muted text-center py-3">No {{ s }} applications.</p>

        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DriveApplications',
  data() {
    return {
      applications: { Applied: [], Shortlisted: [], Interview: [], Offer: [], Placed: [], Rejected: [] },
      message: null,
      statuses: ['Applied', 'Shortlisted', 'Interview', 'Offer', 'Placed', 'Rejected']
    }
  },
  methods: {
    async fetchApplications() {
      const id = this.$route.params.id
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/drive-applications/${id}`, {
        headers: { 'Authentication-Token': localStorage.getItem('token') }
      })
      if (res.ok) this.applications = await res.json()
      else if (res.status === 401) this.$router.push('/login')
    },
    async setStatus(app_id, status, extra = {}) {
      const res = await fetch(`${import.meta.env.VITE_API_URL}/api/update-application/${app_id}`, {
        method: 'POST',
        headers: { 'Authentication-Token': localStorage.getItem('token'), 'Content-Type': 'application/json' },
        body: JSON.stringify({ status, ...extra })
      })
      const data = await res.json()
      this.message = data.message
      this.fetchApplications()
    },
    scheduleInterview(app) {
      this.setStatus(app.application_id, 'Interview', {
        interview_date: app._iDate || null,
        interview_time: app._iTime || '',
        interview_venue: app._iVenue || ''
      })
    },
    markPlaced(app) {
      this.setStatus(app.application_id, 'Placed', {
        joining_date: app._joiningDate || null,
        offer_letter_url: app._offerUrl || ''
      })
    }
  },
  mounted() { this.fetchApplications() }
}
</script>
