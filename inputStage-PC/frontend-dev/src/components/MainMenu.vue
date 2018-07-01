<template>
    <div class="main-menu">
        <img src="../assets/logo.png">
        <h3>Subliminal Sensor System status: {{ senStatus }}</h3>
        <h3>Superliminal Limb System status: {{ motStatus }}</h3>
        <h3>Calibration status: {{ calibStatus }}</h3>
        <h3>Select an action</h3>
        <router-link to="/calibrate">Calibrate muscle map</router-link>
        <router-link to="/monitor">Live synergy monitor</router-link>
        <router-link to="/shutdown">Turn off Subliminal Sensor System</router-link>

        <myFooter></myFooter>
    </div>
</template>

<script>
import axios from 'axios'
import myFooter from './myFooter.vue'

export default {
  name: 'MainMenu',
  data () {
    return {
      senStatus: 'Unknown',
      motStatus: 'Unknown',
      calibStatus: 'Unknown'
    }
  },
  created () {
    this.getSystemStatus()
  },
  components: {
    myFooter
  },
  methods: {
    getSystemStatus () {
      const path = '/api/systemStatus'
      axios.get(path)
        .then(response => {
          this.senStatus = response.data.sensorStatus
          this.motStatus = response.data.motionStatus
          this.calibStatus = response.data.calibStatus
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
  position: relative;
  flex-flow: column nowrap;
  justify-content: center;
  align-items: center;
  height: 100vh;
  img {
    width: 60vw;
  }
}
</style>
