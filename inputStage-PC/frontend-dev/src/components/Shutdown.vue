<template>
    <div class="shutdown">
        <p>It's now safe to turn off your</p>
        <p>Subliminal Sensor System.</p>
    </div>
</template>

<script>
import axios from 'axios'

export default {
  created () {
    this.sendShutdown()
  },
  methods: {
    sendShutdown () {
      const path = '/api/shutdown'
      axios.post(path).catch(error => {
        console.log(error)
      })
    }
  }
}
</script>

<style lang="scss" scoped>
.shutdown {
  background-color: black;
  display: flex;
  flex-flow: column nowrap;

  justify-content: center;
  align-items: center;
  height: 100vh;

  p {
    color: #ff7500;
    font-family: "lores-15", sans-serif;
    font-size: 4vw;
    transform: scaleX(1.2);
    line-height: 1.1;
  }

  p:last-of-type {
    margin-bottom: 12vh;
  }
}
</style>
