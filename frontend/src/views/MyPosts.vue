<template>
  <div class="my-posts-page">
    <div class="page-header">
      <h1>{{ t('myPosts.title') }}</h1>
      <p class="subtitle" v-if="total > 0">{{ t('myPosts.count', { count: total }) }}</p>
    </div>

    <PostList
      :api-endpoint="'/v1/posts/my'"
      :empty-title="t('myPosts.noPosts')"
      :empty-message="t('myPosts.createFirst')"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import PostList from '@/components/PostList.vue'

const { t } = useI18n()
const total = ref(0)
</script>

<style scoped>
.my-posts-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.page-header {
  margin-bottom: 20px;
  padding: 0 4px;
}

.page-header h1 {
  font-size: 28px;
  font-weight: 600;
  margin-bottom: 8px;
  color: #1c1c1c;
}

.subtitle {
  color: #7c7c7c;
  font-size: 14px;
}
</style>
