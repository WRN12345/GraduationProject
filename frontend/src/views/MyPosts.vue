<template>
  <div class="my-posts-page">
    <div class="page-header">
      <h1>我的帖子</h1>
      <p class="subtitle" v-if="total > 0">共 {{ total }} 个帖子</p>
    </div>

    <PostList
      :api-endpoint="'/v1/posts/my'"
      :empty-title="'还没有发布任何帖子'"
      :empty-message="'快去创建你的第一个帖子吧！'"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import PostList from '@/components/PostList.vue'

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
