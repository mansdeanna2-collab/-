// #ifdef VUE3
import { createSSRApp } from 'vue'
import App from './App.hbuilder.vue'

export function createApp() {
  const app = createSSRApp(App)
  return {
    app
  }
}
// #endif

// #ifndef VUE3
import Vue from 'vue'
import App from './App.hbuilder.vue'

Vue.config.productionTip = false

const app = new Vue({
  ...App
})
app.$mount()
// #endif
