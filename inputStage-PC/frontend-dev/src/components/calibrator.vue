<template>
  <div class="calibrator">
    <h1>{{ msg }}</h1>
  </div>
</template>

<script>
export default {
  data () {
    return {
      msg: 'Follow the instructions as they appear.'
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

    this.currentMovement = 0
    this.currentDelay = 0

    setTimeout(this.guide, 5000)
  },
  methods: {
    guide () {
      if (this.currentMovement < 5) {
        let nextMessage = null
        switch (this.currentDelay) {
          case 0:
            nextMessage = 'Ready? Next movement: '
            break
          case 1:
            nextMessage = 'Begin: '
            break
          case 2:
            nextMessage = 'Hold: '
            break
          case 3:
            nextMessage = 'Release: '
            break
        }

        this.msg = nextMessage + this.movements[this.currentMovement]
        setTimeout(this.guide, this.delays[this.currentDelay] * 1000)
        this.currentDelay += 1
        if (this.currentDelay === 4) {
          this.currentDelay = 0
          this.currentMovement += 1
        }

      }
      else {
        this.msg = 'Calibration complete'
        setTimeout(()=>{
          this.$router.push('/')
        }, 3000)
      }
    }
  }
}
</script>

<style lang="scss">
</style>
