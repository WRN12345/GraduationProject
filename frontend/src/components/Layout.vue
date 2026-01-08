<script setup>
import Header from './Header.vue'
import Aside from './Aside.vue'
import Main from './Main.vue'
</script>

<template>
  <div class="app-layout">
    <div class="layout-header">
      <Header />
    </div>
    

    <div class="layout-body">
      <div class="layout-aside">
        <Aside />
      </div>
      

      <div class="layout-main">
        <Main />
      </div>
    </div>
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-header {
  position: sticky;
  top: 0;
  z-index: 1000;
  background: #edeff1;
  border-bottom: 1px solid white;
}

.layout-body {
  display: flex;
  justify-content: center; 
  max-width: 100%;
  padding-top: 20px;
}

.layout-aside {
  width: 270px;
  display: none; 
  padding: 0 10px;

}

.layout-main {
  flex: 1;
  max-width: 980px; 
  display: flex;
  gap: 24px;
  padding: 0 24px;
}

@media (min-width: 960px) {
  .layout-aside {
    display: block;
  }
}
</style>