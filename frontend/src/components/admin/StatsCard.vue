<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  value: {
    type: [Number, String],
    default: 0
  },
  subtitle: {
    type: String,
    default: ''
  },
  icon: {
    type: Object,
    default: null
  },
  color: {
    type: String,
    default: '#0079d3'
  }
})
</script>

<template>
  <div class="stats-card">
    <div class="stats-content">
      <div class="stats-title">{{ title }}</div>
      <div class="stats-value" :style="{ color }">{{ value }}</div>
      <div v-if="subtitle" class="stats-subtitle">{{ subtitle }}</div>
    </div>
    <div v-if="icon" class="stats-icon" :style="{ color }">
      <component :is="icon" :size="28" />
    </div>
  </div>
</template>

<style scoped>
.stats-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color-light);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  transition: box-shadow 0.2s;
}

.stats-card:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.stats-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stats-title {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.stats-value {
  font-size: 28px;
  font-weight: 700;
  line-height: 1.2;
}

.stats-subtitle {
  font-size: 12px;
  color: var(--text-tertiary);
  margin-top: 2px;
}

.stats-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background: var(--bg-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
</style>
