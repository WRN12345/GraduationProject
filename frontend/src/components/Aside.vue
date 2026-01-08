<template>
  <aside class="sidebar">
    <nav class="nav-group">
      <div class="nav-item active"><span class="icon">🏠</span> 主页</div>
      <div class="nav-item"><span class="icon">↗️</span> 受欢迎</div>
      <div class="nav-item"><span class="icon">♾️</span> 浏览</div>
      <div class="nav-item"><span class="icon">🌐</span> 全部</div>
      <div class="nav-item"><span class="icon">➕</span> 加入社区</div>
    </nav>
    
    <div class="divider"></div>

    <div class="section-title">社区</div>
    <nav class="nav-group">
      <div class="nav-item"><span class="icon">🛡️</span>我的社区</div>
      <div class="nav-item"><span class="icon">⚙️</span>设置</div>
    </nav>

    <div class="divider"></div>
    <div class="section-title">隐私</div>
    <nav class="nav-group">
      <div class="nav-item"><span class="icon">🔒</span> 隐私设置</div>
      <div class="nav-item"><span class="icon">🛡️</span> 安全中心</div>
      <div class="nav-item"><span class="icon">👀</span> 历史记录</div>
      <div class="nav-item"><span class="icon">🔖</span> 收藏夹</div>
    </nav>
    <div class="divider"></div>
  </aside>
</template>

<style scoped>
.sidebar {
  padding-bottom: 20px;
}

.nav-item {
  padding: 10px 12px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 12px;
  color: #1c1c1c;
  font-size: 14px;
}

.nav-item:hover {
  background-color: #f6f7f8;
}

.nav-item.active {
  background-color: #f6f7f8;
  font-weight: 600;
}

.divider {
  height: 1px;
  background-color: #edeff1;
  margin: 15px 0;
}

.section-title {
  font-size: 12px;
  color: #878a8c;
  text-transform: uppercase;
  font-weight: 700;
  margin-bottom: 8px;
  padding-left: 12px;
}
</style>