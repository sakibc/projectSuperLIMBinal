<template>
  <div class="chartHolder">
    <canvas :id="id"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js'

export default {
  data () {
    return {
      id: null
    }
  },
  created () {
    this.id = 'emg-chart-'.concat(this._uid)
  },
  mounted () {
    var ctx = document.getElementById(this.id).getContext('2d')

    // eslint-disable-next-line
    var myChart = new Chart(ctx, {
      type: 'line'
    })
  }
}
</script>

<style lang="scss">
  .chartHolder {
    width: 25vw;
    position: relative;
  }
</style>
