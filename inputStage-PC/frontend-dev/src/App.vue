<template>
  <div id="app">
    <transition :name="transitionName">
      <router-view/>
    </transition>
  </div>
</template>

<script>
export default {
  data () {
    return {
      transitionName: 'slide-in'
    }
  },
  name: 'App',
  watch: {
    '$route' (to, from) {
      if (to.path === '/') {
        this.transitionName = 'slide-out'
      } else {
        this.transitionName = 'slide-in'
      }
    }
  }
}
</script>

<style lang="scss">
@import 'styles/reset';
@import 'styles/transitions';

// body {
//   height: 100vh;
// }

#app {
  font-family: "europa", Helvetica, Arial, sans-serif;
  font-style: normal;
  font-weight: 400;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  background-color: #f5f5f5;
}

.page {
  position: absolute;
}

</style>
