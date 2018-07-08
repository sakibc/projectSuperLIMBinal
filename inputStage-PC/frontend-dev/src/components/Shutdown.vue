<template>
    <div class="shutdown page">
        <p>It's now safe to turn off your</p>
        <p>Subliminal Sensor System.</p>
    </div>
</template>

<script>
export default {
  created () {
    this.sendShutdown()
  },
  methods: {
    sendShutdown () {
      this.$socket.emit('shutdown')
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
  width: 100vw;

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
