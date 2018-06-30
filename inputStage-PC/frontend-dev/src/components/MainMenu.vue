<template>
    <div class="main-menu">
        <img src="../assets/logo.png">
        <h3>Subliminal Sensor System status: {{ senStatus }}</h3>
        <h3>Superliminal Limb System status: {{ motStatus }}</h3>
        <h3>Select an action</h3>
        <router-link to="/calibrate">Calibrate muscle map</router-link>
        <router-link to="/monitor">Live synergy monitor</router-link>
        <router-link to="/shutdown">Turn off Subliminal Sensor System</router-link>
    </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'MainMenu',
  data () {
    return {
      senStatus: 'Unknown',
      motStatus: 'Unknown'
    }
  },
  created () {
    this.getSystemStatus()
  },
  methods: {
    getSystemStatus () {
      const path = '/api/systemStatus'
      axios.get(path)
        .then(response => {
          this.senStatus = response.data.sensorStatus
          this.motStatus = response.data.motionStatus
        })
        .catch(error => {
          console.log(error)
        })
    }
  }
}
</script>

<style lang="scss" scoped>
.main-menu {
  display: flex;
  flex-flow: column nowrap;
  justify-content: center;
  align-items: center;
  height: 100vh;
  img {
    width: 40vw;
  }
}
</style>
