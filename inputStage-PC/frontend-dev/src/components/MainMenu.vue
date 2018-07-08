<template>
  <div class="wrapper page">
    <div class="main-menu">
      <logoHolder></logoHolder>

      <div v-if="calibLoaded || calibLoadFailed" class="card">
        <h3 v-if="calibLoaded" class="pos">Calibration matrix loaded.</h3>
        <h3 v-else-if="calibLoadFailed" class="neg">Calibration matrix load failed!</h3>
      </div>

      <div class="card status-card">
        <div class="status">
          <h3>Subliminal Sensor System:</h3>
          <h3>Superliminal Limb System:</h3>
          <h3>Calibration status:</h3>
        </div>
        <div class="status">
          <h3 v-if="sensStatus" class="pos">Connected</h3>
          <h3 v-else class="neg">Disconnected</h3>
          <h3 v-if="motStatus" class="pos">Connected</h3>
          <h3 v-else class="neg">Disconnected</h3>
          <h3 v-if="calibStatus" class="pos">Calibrated</h3>
          <h3 v-else class="neg">Not calibrated</h3>
        </div>
      </div>

      <div class="card">
        <h3>Select an action</h3>
        <div class="menu">
          <router-link to="/calibrate" v-if="!calibStatus && sensStatus">Calibrate muscle map</router-link>
          <router-link to="/calibrate" v-if="calibStatus && sensStatus">Recalibrate muscle map</router-link>
          <button v-on:click="loadMatrix()" v-if="!calibStatus && sensStatus">Load last calibration matrix</button>
          <router-link to="/monitor" v-if="calibStatus && sensStatus">Live synergy monitor</router-link>
        </div>
        <div class="menu">
          <router-link to="/shutdown">Turn off Sensor System</router-link>
          <router-link to="/restart">Restart Sensor System</router-link>
        </div>
      </div>
    </div>

    <myFooter></myFooter>
  </div>
</template>

<script>
// import axios from 'axios'
import myFooter from './myFooter.vue'
import logoHolder from './logoHolder.vue'

export default {
  name: 'MainMenu',
  data () {
    return {
      sensStatus: false,
      motStatus: false,
      calibStatus: false,
      calibLoaded: false,
      calibLoadFailed: false
    }
  },
  created () {
    this.getSystemStatus()
  },
  components: {
    myFooter,
    logoHolder
  },
  sockets: {
    systemStatus (data) {
      this.sensStatus = data.sensorStatus
      this.motStatus = data.motionStatus
      this.calibStatus = data.calibStatus
    },
    loadMatrix (data) {
      this.calibLoaded = data.calibLoaded
      this.calibLoadFailed = data.calibLoadFailed

      this.getSystemStatus()
      setTimeout(this.dismissCalibLoadMessage, 3000)
    }
  },
  methods: {
    getSystemStatus () {
      // const path = '/api/systemStatus'
      // axios
      //   .get(path)
      //   .then(response => {

      //   })
      //   .catch(error => {
      //     console.log(error)
      //   })
      this.$socket.emit('systemStatus')
    },
    loadMatrix () {
      this.$socket.emit('loadMatrix')
    },
    dismissCalibLoadMessage () {
      this.calibLoaded = false
      this.calibLoadFailed = false
    }
  }
}
</script>

<style lang="scss" scoped>
@import "../styles/colors";
.neg {
  color: darkred;
}
.pos {
  color: $subliminal-blue;
}

.main-menu {
  display: flex;
  flex-grow: 1;
  position: relative;
  max-width: 1024px;
  flex-flow: column nowrap;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
  h3 {
    line-height: 1.2;
  }

  .menu {
    display: flex;
    flex-flow: column nowrap;
    margin-top: 10px;

    @media only screen and (min-width: 600px) {
      margin-left: 20px;
      margin-top: 0px;
    }
  }
}
.status {
  display: flex;
  flex-flow: column nowrap;
  text-align: right;
  justify-content: center;
}
.card {
  flex-flow: column nowrap;
  justify-content: center;
  margin-top: 20px;
  padding: 20px;
  background: #fdfdfd;
  width: 90vw;

  @media only screen and (min-width: 600px) {
    width: 70vw;
    flex-flow: row nowrap;
  }
  @media only screen and (min-width: 900px) {
    width: 630px;
  }

  border-radius: 8px;
  box-shadow: 3px 5px 20px rgba(0, 0, 0, 0.05);
  display: flex;
  a, button {
    padding: 10px;
    margin-bottom: 10px;
    box-shadow: 3px 5px 20px rgba(0, 0, 0, 0.1);
    background: $subliminal-pale;
    border-radius: 8px;
    color: $slightly-white;
    text-decoration: None;
    transition: all .2s;
    &:hover {
      background: $subliminal-blue;
      transform: scale(1.02);
    }
    &:active {
      background: $subliminal-dark;
      box-shadow: None;
    }
  }
  a:last-of-type {
    margin-bottom: 0px;
  }
  button {
    font-family: 'europa', Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1;
    margin-top: 10px;
    border: None;
  }
  .status:last-of-type {
    margin-left: 20px;
    text-align: left;
  }
}
.status-card {
  flex-flow: row nowrap;
}
.wrapper {
  display: flex;
  flex-flow: column nowrap;
  min-height: 100vh;
  justify-content: space-between;
  align-items: center;
  background: $kinda-grey;
}

</style>
