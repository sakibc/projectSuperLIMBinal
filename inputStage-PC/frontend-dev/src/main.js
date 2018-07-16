// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

import socketio from 'socket.io-client'
import VueSocketIO from 'vue-socket.io'

export let SocketInstance = global.SocketInstance

if (process.env.NODE_ENV === 'development') {
  SocketInstance = socketio('http://localhost:5000')
} else {
  SocketInstance = socketio()
}

Vue.config.productionTip = false
Vue.use(VueSocketIO, SocketInstance)

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
