<template>
    <div class="shutdown page">
      <transition name="crt-in" appear>
        <div>
          <p>It's now safe to turn off your</p>
          <p>Subliminal Sensor System.</p>
        </div>
      </transition>
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

    filter: blur(0.5px) drop-shadow(0 0 2px #ff7500);
    // animation: 
  }

  p:last-of-type {
    margin-bottom: 12vh;
  }

  .crt-in-enter {
    filter: blur(0) drop-shadow(0 0 0 #ff7500);
    opacity: 0;
  }
  .crt-in-enter-active {
    transition-property: filter, opacity;
    transition-duration: 5s;
    transition-timing-function: ease-in-out, ease-out;
  }
}
</style>
