<template>
  <div class="card">
    <div class="card-header">
      <h3>{{ usertype.charAt(0).toUpperCase() + usertype.slice(1) }}s</h3>
    </div>
    <div class="card-body">
      <div v-if="users">
        <ul v-if="users" class="nav nav-pills mb-3" id="pills-tab" role="tablist">
          <li v-for="(status, index) in getStatuses()" :key="status" class="nav-item me-3" role="presentation">
            <button class="nav-link" :class="{ active: index === 0 }" :id="`pills-${status}-tab`"
              data-bs-toggle="pill" :data-bs-target="`#pills-${status}-${usertype}`"
              type="button" role="tab" :aria-controls="`pills-${status}`" aria-selected="true">
              {{ status }}
            </button>
          </li>
        </ul>
        <div v-if="users" class="tab-content" id="pills-tabContent">
          <div v-for="(status, index) in getStatuses()" class="tab-pane fade"
            :class="{ 'show active': index === 0 }" :key="status"
            :id="`pills-${status}-${usertype}`" role="tabpanel"
            :aria-labelledby="`pills-${status}-tab`" tabindex="0">
            <UsersTable :perticular_users="get_perticular_users(status)" :usertype="usertype" @refresh="$emit('refresh')" />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import UsersTable from './UsersTable.vue'

export default ({
  name: 'UsersCard',
  props: {
    users: { type: Object, required: true },
    usertype: { type: String, required: true }
  },
  components: { UsersTable },
  methods: {
    getStatuses() {
      return Object.keys(this.users)
    },
    get_perticular_users(status) {
      return { status: status, users: this.users[status] }
    }
  }
})
</script>
