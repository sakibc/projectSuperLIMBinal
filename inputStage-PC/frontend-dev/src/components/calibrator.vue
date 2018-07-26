<template>
  <div class="calibrator">
    <transition name="caliguide" appear>
      <h1 id="msgText">{{ msg }}</h1>
    </transition>
    <div id="calibTimerBar"></div>
  </div>
</template>

<script>
import anime from 'animejs'

export default {
  data () {
    return {
      msg: 'Follow the instructions as they appear.'
    }
  },
  watch: {
    msg: function (newValue) {
      if (this.bounce) {
        this.msgAni = anime.timeline()
        this.msgAni
        .add({
          targets: '#msgText',
          translateY: '-10px',
          duration: 100,
          easing: 'easeOutQuad'
        })
        .add({
          targets: '#msgText',
          translateY: 0,
          duration: 100,
          easing: 'easeInQuad'
        })
        .add({
          targets: '#msgText',
          translateY: '-5px',
          duration: 100,
          easing: 'easeOutQuad'
        })
        .add({
          targets: '#msgText',
          translateY: 0,
          duration: 100,
          easing: 'easeInQuad'
        })
      }
    }
  },
  mounted () {
    this.movements = [
      'Rest',
      'Open Hand',
      'Close Hand',
      'Pronate',
      'Supinate'
    ]
    this.delays = [2, 2, 3, 2]
    this.timerBar = document.getElementById('calibTimerBar')

    this.currentMovement = 0
    this.currentDelay = 0

    this.bounce = false
    let that = this
    setTimeout(function () {
      that.bounce = true // this is dumb...
    }, 6000)

    this.timerBarAni = anime({
      targets: '#calibTimerBar',
      scaleX: [0, 1],
      duration: 50000,
      easing: 'linear',
    })

    this.msgAni = anime.timeline()
    this.msgAni
    .add({
      targets: '#msgText',
      translateY: '20px',
      opacity: [1,0],
      duration: 400,
      offset: 4600,
      easing: 'easeInQuad'
    })
    .add({
      targets: '#msgText',
      opacity: [0,1],
      translateY: 0,
      duration: 400,
      offset: 5400,
      easing: 'easeOutQuad'
    })

    this.guideTimer = setTimeout(this.guide, 5000)
  },
  beforeDestroy () {
    clearInterval(this.guideTimer)
  },
  methods: {
    guide () {
      let that = this

      if (this.currentMovement < 5) {
        let nextMessage = null
        switch (this.currentDelay) {
          case 0:
            nextMessage = 'Ready? Next movement: '
            this.timerBar.style.backgroundColor = '#008ade'

            setTimeout(function () {
              that.bounce = true // this is dumb...
            }, 1000)
            break
          case 1:
            nextMessage = 'Begin '
            this.timerBar.style.backgroundColor = 'orange'
            break
          case 2:
            nextMessage = 'Hold '
            this.timerBar.style.backgroundColor = 'red'
            break
          case 3:
            nextMessage = 'Release '
            this.timerBar.style.backgroundColor = '#7cd6ff'

            setTimeout(function () {
              that.bounce = false // this is dumb...
            }, 1000)

            this.msgAni = anime.timeline()
            this.msgAni
            .add({
              targets: '#msgText',
              translateY: '20px',
              opacity: [1,0],
              duration: 400,
              offset: 1600,
              easing: 'easeInQuad'
            })
            .add({
              targets: '#msgText',
              opacity: [0,1],
              translateY: 0,
              duration: 400,
              offset: 2400,
              easing: 'easeOutQuad'
            })
            break
        }

        this.msg = nextMessage + this.movements[this.currentMovement]
        this.guideTimer = setTimeout(this.guide, this.delays[this.currentDelay] * 1000)
        this.currentDelay += 1
        if (this.currentDelay === 4) {
          this.currentDelay = 0
          this.currentMovement += 1
        }

      }
      else {
        this.msg = 'Calibration complete'
        this.timerBar.style.backgroundColor = 'limeGreen'
        setTimeout(()=>{
          this.msg = 'Processing...'
        }, 3000)
      }
    }
  }
}
</script>

<style lang="scss">
@import "../styles/colors";

.calibrator {
  position: relative;
  flex-grow: 1;
  display: flex;
  justify-content: center;
  align-items: center;

  #calibTimerBar {
    position: absolute;
    left: -20px;
    width: calc(100% + 40px);
    transform-origin: bottom left;
    bottom: -20px;
    height: 12px;
    background: $subliminal-blue;
    transition: background-color 0.2s ease;
  }
}
</style>
