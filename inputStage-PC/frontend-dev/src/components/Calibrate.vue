<template>
  <div class='calibration page'>
    <div class='card'>
      <h2>Muscle Map Calibration</h2>
      <div class="charts">
        <emgChart
          v-for="(signal, index) in emgSignals"
          :key="'emg-' + index"
          :emgId="'emg-' + index"
          :emgSignal='signal'
          :title='titles[index]'
        ></emgChart>
      </div>
    </div>
    <div class='card'>
      <calibrator></calibrator>
    </div>

  </div>
</template>

<script>
// import axios from 'axios'

import myFooter from './myFooter.vue'
import emgChart from './emgChart.vue'
import calibrator from './calibrator.vue'

const Fs = 601 // the amount of samples in ten seconds (streamed slow enough so the graph can draw it)

export default {
  data () {
    return {
      emgSignals: [
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} })],

      titles: [
        'Flexor carpi ulnaris',
        'Flexor carpi radialis',
        'Extensor carpi ulnaris',
        'Extensor carpi radialis',
        'Flexor digitorum superficialis 1',
        'Flexor digitorum superficialis 2',
        'Flexor digitorum superficialis 3',
        'Flexor digitorum superficialis 4',
      ]
    }
  },
  components: {
    myFooter,
    emgChart,
    calibrator
  },
  sockets: {
    receiveSample (data) {
      for (var i = 0; i < 8; i++) {
        let newData = {x: this.t, y: data[i][0]}
        this.emgSignals[i].push(newData)
        this.emgSignals[i].shift()
      }
      this.t += 1
    }
  },
  created () {
    this.startCalibration()
  },
  mounted () {
    this.startSampleRequest()
  },
  beforeDestroy () {
    this.stopSampleRequest()
  },
  methods: {
    startCalibration () {
      this.$socket.emit('startCalibration')
    },
    requestSample () {
      this.$socket.emit('getSample')
    },
    startSampleRequest () {
      this.requestTimer = setInterval(this.requestSample, 10)
      this.t = 0
    },
    stopSampleRequest () {
      clearInterval(this.requestTimer)
      this.$socket.emit('abortCalibration') // TODO: make this functional
    }
  }
}
</script>

<style lang='scss'>
@import '../styles/elements';

.calibration {
  // height: 100vh;
  position: relative;
  display: flex;
  flex-flow: column;
  padding: 20px;

  h2 {
    margin-bottom: 20px;
  }

  .card:first-of-type {
    margin-top: 0;
  }
}
.charts {
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
}
</style>
