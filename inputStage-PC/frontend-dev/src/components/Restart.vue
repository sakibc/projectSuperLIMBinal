<template>
    <div class="wrapper page">
      <div class="restart">
        <div class="card">
          <h3>Restarting...</h3>
          <div class="progress-bg">
            <div id="progress-bar"></div>
          </div>
        </div>
      </div>
      <myFooter></myFooter>
    </div>
</template>

<script>
import anime from 'animejs'
import myFooter from './myFooter.vue'

export default {
  created () {
    this.sendRestart()
    this.goBack()
  },
  mounted () {
    this.progressBarAni = anime({
      targets: '#progress-bar',
      width: '100%',
      duration: 30000,
      easing: 'linear'
    })
  },
  components: {
    myFooter
  },
  methods: {
    sendRestart () {
      this.$socket.emit('restart')
    },
    goBack () {
      setTimeout(() => this.$router.push('/'), 30000)
    }
  }
}
</script>

<style lang="scss" scoped>
@import "../styles/colors";
@import "../styles/elements";

  .restart {
    width: 100vw;
    background: $kinda-grey;
    display: flex;
    flex-flow: column nowrap;
    justify-content: center;
    align-items: center;
    flex-grow: 1;

    .card {
      flex-flow: column nowrap;
    }

    footer {
      position: absolute;
      bottom: 0;
      left: 0;
    }
  }

  #progress-bar {
    width: 0%;
    height: 30px;
    background: $subliminal-pale;
    border-radius: 4px;
    box-shadow: 3px 5px 20px rgba(0, 0, 0, 0.1);
  }

  .progress-bg {
    margin-top: 20px;
    padding: 4px;
    width: 70vw;
    max-width: 630px;
    background: $kinda-grey;
    border-radius: 8px;
    box-shadow: inset 3px 5px 20px rgba(0, 0, 0, 0.1);
  }
</style>
