import Vue from 'vue'
import Router from 'vue-router'
import MainMenu from '@/components/MainMenu'
import Calibrate from '@/components/Calibrate'
import Monitor from '@/components/Monitor'
import Shutdown from '@/components/Shutdown'

Vue.use(Router)

export default new Router({
  routes: [
    { path: '/', component: MainMenu },
    { path: '/calibrate', component: Calibrate },
    { path: '/monitor', component: Monitor },
    { path: '/shutdown', component: Shutdown }
  ]
})
