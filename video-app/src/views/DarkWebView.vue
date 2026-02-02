<template>
  <div class="page-container">
    <div class="page-header">
      <h1>{{ title }}</h1>
      <p class="subtitle">{{ subtitle }}</p>
    </div>
    
    <div class="coming-soon">
      <div class="icon">{{ icon }}</div>
      <h2>即将上线</h2>
      <p>精彩内容正在准备中，敬请期待...</p>
      <router-link to="/" class="btn btn-primary">返回首页</router-link>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DarkWebView',
  data() {
    return {
      title: '暗网专区',
      subtitle: '探索未知领域',
      icon: '🌐'
    }
  }
}
</script>

<style scoped>
.page-container {
  min-height: 100vh;
  padding: 20px;
  padding-bottom: 80px;
}

.page-header {
  text-align: center;
  padding: 30px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 1.8em;
  margin-bottom: 10px;
  background: linear-gradient(90deg, #00d4ff, #7c3aed);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #888;
  font-size: 0.9em;
}

.coming-soon {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  text-align: center;
}

.icon {
  font-size: 4em;
  margin-bottom: 20px;
}

.coming-soon h2 {
  font-size: 1.5em;
  margin-bottom: 10px;
  color: #fff;
}

.coming-soon p {
  color: #888;
  margin-bottom: 30px;
}

@media (max-width: 480px) {
  .page-header h1 {
    font-size: 1.4em;
  }
  
  .icon {
    font-size: 3em;
  }
  
  .coming-soon h2 {
    font-size: 1.2em;
  }
}
</style>
