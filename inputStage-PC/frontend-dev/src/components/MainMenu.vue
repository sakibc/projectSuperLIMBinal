<template>
  <div class="wrapper page">
    <div class="main-menu">
      <logoHolder id="logoHolder"></logoHolder>

      <transition name="cardIn2"
      v-on:before-enter="setupNewCardAni"
      v-on:enter="animateNewCard"
      v-on:leave="setupNewCardAni"
      v-on:after-leave="animateNewCard">
        <div v-if="calibLoaded || calibLoadFailed" class="card">
          <h3 v-if="calibLoaded" class="pos">Calibration matrix loaded.</h3>
          <h3 v-else-if="calibLoadFailed" class="neg">Calibration matrix load failed!</h3>
        </div>
      </transition>
      
      <transition name="cardIn" appear>
        <div class="card status-card" id="status-card">
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
      </transition>

      <transition name="cardIn" appear>
        <div class="card" id="menu-card">
          <h3>Select an action</h3>
          <div class="menu">
            <router-link to="/calibrate" v-if="!calibStatus && sensStatus">Calibrate muscle map</router-link>
            <router-link to="/calibrate" v-if="calibStatus && sensStatus">Recalibrate muscle map</router-link>
            <button v-on:click="loadMatrix()" v-if="!calibStatus && sensStatus">Load last calibration matrix</button>
            <router-link to="/monitor" v-if="calibStatus && sensStatus">Move Prosthetic Limb</router-link>
          </div>
          <div class="menu">
            <router-link to="/shutdown">Turn off Sensor System</router-link>
            <router-link to="/restart">Restart Sensor System</router-link>
          </div>
        </div>
      </transition>
    </div>

    <transition name="footer" appear>
      <myFooter id="myFooter"></myFooter>
    </transition>
  </div>
</template>

<script>
// import axios from 'axios'
import myFooter from './myFooter.vue'
import logoHolder from './logoHolder.vue'
import anime from 'animejs'

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
    this.checkStatus = setInterval(this.getSystemStatus, 1000)
  },
  beforeDestroy () {
    clearInterval(this.checkStatus)
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
      this.$socket.emit('systemStatus')
    },
    loadMatrix () {
      this.$socket.emit('loadMatrix')
    },
    dismissCalibLoadMessage () {
      this.calibLoaded = false
      this.calibLoadFailed = false
    },
    animateNewCard () {
      let statusCardPos1 = this.statusCard.getBoundingClientRect()
      let menuCardPos1 = this.menuCard.getBoundingClientRect()
      let logoHolderPos1 = this.logoHolder.getBoundingClientRect()
      let myFooterPos1 = this.myFooter.getBoundingClientRect()

      let statusInvertedTop = this.statusCardPos0.top - statusCardPos1.top
      this.statusCard.style.transformOrigin = 'top left'
      
      anime({
        targets: '#status-card',
        translateY: [statusInvertedTop, 0],
        duration: 400,
        easing: 'easeInOutQuad'
      })

      let menuInvertedTop = this.menuCardPos0.top - menuCardPos1.top
      this.menuCard.style.transformOrigin = 'top left'
      
      anime({
        targets: '#menu-card',
        translateY: [menuInvertedTop, 0],
        duration: 400,
        easing: 'easeInOutQuad'
      })

      let logoHolderInvertedTop = this.logoHolderPos0.top - logoHolderPos1.top
      this.logoHolder.style.transformOrigin = 'top left'
      
      anime({
        targets: '#logoHolder',
        translateY: [logoHolderInvertedTop, 0],
        duration: 400,
        easing: 'easeInOutQuad'
      })

      let myFooterInvertedTop = this.myFooterPos0.top - myFooterPos1.top
      this.myFooter.style.transformOrigin = 'top left'
      
      anime({
        targets: '#myFooter',
        translateY: [myFooterInvertedTop, 0],
        duration: 400,
        easing: 'easeInOutQuad'
      })
    },
    setupNewCardAni () {
      this.statusCard = document.getElementById('status-card')
      this.menuCard = document.getElementById('menu-card')
      this.logoHolder = document.getElementById('logoHolder')
      this.myFooter = document.getElementById('myFooter')

      this.statusCardPos0 = this.statusCard.getBoundingClientRect()
      this.menuCardPos0 = this.menuCard.getBoundingClientRect()
      this.logoHolderPos0 = this.logoHolder.getBoundingClientRect()
      this.myFooterPos0 = this.myFooter.getBoundingClientRect()
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
    margin-bottom: 0px;
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

.footer-enter-active, .footer-leave-active {
  transition: transform 0.4s;
  transition-delay: 0.4s;
  transition-timing-function: ease-out;
}

.footer-enter, .footer-leave-to {
  transform: translate3d(0,100%,0)
}

.cardIn-enter-active, .cardIn-leave-active {
  transition: all 0.4s;
  transition-delay: 0.4s;
  transition-timing-function: ease-in-out;
}

.cardIn-enter, .cardIn-leave-to {
  transform: translate3d(0, 10px, 0);
  opacity: 0;
}

.cardIn2-enter-active, .cardIn2-leave-active {
  // whatever...
  transition: all 0.4s;
  transition-timing-function: ease-in-out;
}

.cardIn2-enter, .cardIn2-leave-to {
  transform: translate3d(0, 10px, 0);
  opacity: 0;
}

</style>
