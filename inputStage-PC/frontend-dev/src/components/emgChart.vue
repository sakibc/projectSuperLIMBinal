<template>
  <div>
    <div class="myChart" :id="emgId"></div>
    <p>{{ title }}</p>
  </div>
</template>

<script>
import Rickshaw from 'rickshaw'

export default {
  props: {
    emgSignal: Array,
    emgId: String,
    title: String
  },
  mounted () {
    this.graph = new Rickshaw.Graph({
      element: document.getElementById(this.emgId),
      renderer: 'line',
      min: 0,
      max: 1,
      interpolation: 'linear',
      series: [
        {
          color: 'steelblue',
          data: this.emgSignal
        }
      ]
    })
    this.graph.render()
    window.requestAnimationFrame(this.updateChart)
  },
  methods: {
    updateChart () {
      this.graph.render()
      window.requestAnimationFrame(this.updateChart)
    }
  }
}
</script>

<style lang='scss' scoped>
.myChart {
  position: relative;
  width: calc((100vw - 100px) / 2);
  height: 100px;
}
</style>
