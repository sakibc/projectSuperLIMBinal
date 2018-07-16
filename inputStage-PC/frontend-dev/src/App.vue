<template>
  <div id='app'>
    <transition :name='transitionName'>
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
    $route (to, from) {
      if (to.path === '/') {
        this.transitionName = 'slide-out'
        // document.body.style.backgroundColor = '#f5f5f5'
      } else if (to.path === '/shutdown') {
        this.transitionName = 'tv'
        // document.body.style.backgroundColor = 'black'
      } else {
        this.transitionName = 'slide-in'
        // document.body.style.backgroundColor = '#f5f5f5'
      }
    }
  }
}
</script>

<style lang='scss'>
@import 'styles/reset';
@import 'styles/transitions';

body {
  background-color: #f5f5f5;
}

#app {
  font-family: 'europa', Helvetica, Arial, sans-serif;
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
  width: 100vw;
  min-height: 100vh;
}
</style>
