<template>
  <div class='monitor page'>
    <div class='card'>
      <h2>Live Synergy Monitor</h2>
      <div class="charts">
        <emgChart
          v-for="(signal, index) in synSignals"
          :key="'syn-' + index"
          :emgId="'syn-' + index"
          :emgSignal='signal'
          :title='titles[index]'
        ></emgChart>
      </div>
    </div>
    <myFooter></myFooter>
  </div>
</template>

<script>
// import axios from 'axios'

import myFooter from './myFooter.vue'
import emgChart from './emgChart.vue'

const Fs = 300 // the amount of samples in ten seconds (streamed slow enough so the graph can draw it)

export default {
  data () {
    return {
      synSignals: [
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} }),
        Array.from(new Array(Fs), (val, i) => { return {x: -Fs + i, y: null} })],

      titles: [
        'Hand Open',
        'Hand Closed',
        'Pronation',
        'Supination'
      ]
    }
  },
  components: {
    myFooter,
    emgChart
  },
  sockets: {
    receiveSample (data) {
      for (var i = 0; i < 4; i++) {
        let newData = {x: this.t, y: data[i][0]}
        this.synSignals[i].push(newData)
        this.synSignals[i].shift()
      }
      this.t += 1
      this.samplesReceived += 1
    }
  },
  created () {
    this.startMonitor()
  },
  mounted () {
    this.startSampleRequest()
    this.samplesReceived = 0
  },
  beforeDestroy () {
    this.stopSampleRequest()
  },
  methods: {
    startMonitor () {
      this.$socket.emit('startMonitor')
    },
    requestSample () {
      this.$socket.emit('getSample')
    },
    startSampleRequest () {
      this.requestTimer = setInterval(this.requestSample, 32)
      this.t = 0
            this.statsTimer = setInterval(this.calculateFreq, 1000)
    },
    calculateFreq () {
      console.log('Broadcast rate: ' + (this.samplesReceived) + ' samples per second.')
      this.samplesReceived = 0
    },
    stopSampleRequest () {
      clearInterval(this.requestTimer)
      clearInterval(this.statsTimer)
      this.$socket.emit('stopMonitor') // TODO: make this functional
      console.log('stopping...')
    }
  }
}
</script>

<style lang='scss'>
@import '../styles/elements';
@import "../styles/colors";

.monitor {
  // height: 100vh;
  position: relative;
  display: flex;
  flex-flow: column;
  padding: 20px;
  
  footer {
      position: absolute;
      bottom: 0;
      left: 0;
  }

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
