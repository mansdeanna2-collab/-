<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <keep-alive include="HomeView">
        <component :is="Component" />
      </keep-alive>
    </router-view>
    <!-- Bottom Navigation - visible except on player page -->
    <BottomNav v-if="showBottomNav" />
  </div>
</template>

<script>
import BottomNav from '@/components/BottomNav.vue'

export default {
  name: 'App',
  components: {
    BottomNav
  },
  computed: {
    showBottomNav() {
      return this.$route.name !== 'player'
    }
  }
}
</script>

<style>
#app {
  width: 100%;
  min-height: 100vh;
}
</style>
