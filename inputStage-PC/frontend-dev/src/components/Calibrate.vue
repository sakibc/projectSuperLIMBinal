<template>
  <div class="calibration">
    <h2>Muscle Map Calibration</h2>

    <div class="chartRow">
      <emgChart></emgChart>
      <emgChart></emgChart>
      <emgChart></emgChart>
      <emgChart></emgChart>
    </div>
    <div class="chartRow">
      <emgChart></emgChart>
      <emgChart></emgChart>
      <emgChart></emgChart>
      <emgChart></emgChart>
    </div>

  </div>
</template>

<script>
import axios from 'axios'

import myFooter from './myFooter.vue'
import emgChart from './emgChart.vue'
export default {
  components: {
    myFooter,
    emgChart
  },
  created () {
    this.startCalibration()
  },
  mounted () {
    this.startSampleRequest()
  },
  methods: {
    startCalibration () {
      const path = '/api/startCalibration'
      axios.post(path).catch(error => {
        console.log(error)
      })
    },
    requestSample () {
      const path = '/api/getSample'
      axios.get(path)
        .then(response => {
          console.log(response)
        })
        .catch(error => {
          console.log(error)
        })
    },
    startSampleRequest () {
      setInterval(this.requestSample, 16)
    }
  }
}
</script>

<style lang="scss">
  .calibration {
    // height: 100vh;
    position: relative;
    display: flex;
    flex-flow: column;
  }
  .chartRow {
    display: flex;
    flex-flow: row nowrap;
  }
</style>
