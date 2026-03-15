/**
 * 投票逻辑 Composable
 *
 * 核心特性：
 * 1. 乐观更新（Optimistic UI）- 点击立即更新 UI
 * 2. 防抖（Debounce）- 500ms 后发送最终状态
 * 3. 点赞点踩互斥 - 自动处理状态转换
 * 4. 回滚机制 - 失败时静默回滚
 */

import { ref, computed, watch, onUnmounted } from 'vue'
import { client } from '@/api/client'
import { ElMessage } from 'element-plus'

export interface VoteState {
  upvotes: number
  downvotes: number
  userVote: 1 | -1 | 0  // 1=赞, -1=踩, 0=无
}

export interface UseVoteOptions {
  targetType: 'post' | 'comment'
  targetId: number
  initialState: VoteState
  debounceMs?: number // 防抖延迟，默认 500ms
}

export function useVote(options: UseVoteOptions) {
  const {
    targetType,
    targetId,
    initialState,
    debounceMs = 500
  } = options

  // 本地状态（使用 internal 前缀避免返回时的命名冲突）
  // 初始化时确保非负数
  const internalState = ref<VoteState>({
    upvotes: Math.max(0, initialState.upvotes),
    downvotes: Math.max(0, initialState.downvotes),
    userVote: initialState.userVote
  })
  const loading = ref(false)

  // 待发送状态（防抖用）
  const pendingDirection = ref<1 | -1 | 0 | null>(null)
  const rollbackState = ref<VoteState | null>(null)

  // 防抖定时器
  let debounceTimer: ReturnType<typeof setTimeout> | null = null

  /**
   * 乐观更新状态计算
   * 处理点赞点踩互斥逻辑
   * 使用局部变量计算，最后一次性赋值新对象，确保 Vue 3 响应式触发
   */
  const updateStateOptimistically = (direction: 1 | -1) => {
    const current = internalState.value.userVote
    let newUpvotes = internalState.value.upvotes
    let newDownvotes = internalState.value.downvotes
    let newUserVote: 1 | -1 | 0 = current

    if (current === direction) {
      // 重复点击 → 取消投票
      if (direction === 1) {
        newUpvotes--
      } else {
        newDownvotes--
      }
      newUserVote = 0
    } else if (current === 0) {
      // 新投票
      if (direction === 1) {
        newUpvotes++
      } else {
        newDownvotes++
      }
      newUserVote = direction
    } else {
      // 改变方向（赞↔踩互斥）
      // 先取消原来的
      if (current === 1) {
        newUpvotes--
      } else {
        newDownvotes--
      }
      // 再设置新的
      if (direction === 1) {
        newUpvotes++
      } else {
        newDownvotes++
      }
      newUserVote = direction
    }

    // 一次性赋值新对象，确保 Vue 检测到变化
    // 使用 Math.max(0, value) 确保非负数
    internalState.value = {
      upvotes: Math.max(0, newUpvotes),
      downvotes: Math.max(0, newDownvotes),
      userVote: newUserVote
    }
  }

  /**
   * 核心投票方法
   * 乐观更新 + 防抖
   */
  const handleVote = async (direction: 1 | -1) => {
    // 1. 保存快照用于回滚
    const previousState = { ...internalState.value }
    rollbackState.value = previousState

    // 2. 立即更新 UI（乐观更新）
    updateStateOptimistically(direction)

    // 3. 计算最终状态
    const current = internalState.value.userVote
    const finalDirection: 1 | -1 | 0 = current

    // 4. 记录待发送状态
    pendingDirection.value = finalDirection

    // 5. 清除之前的防抖定时器
    if (debounceTimer) {
      clearTimeout(debounceTimer)
    }

    // 6. 设置新的防抖定时器
    debounceTimer = setTimeout(async () => {
      await sendVoteToBackend(finalDirection, previousState)
      // 清除待发送状态
      pendingDirection.value = null
      rollbackState.value = null
      debounceTimer = null
    }, debounceMs)
  }

  /**
   * 发送投票请求到后端
   */
  const sendVoteToBackend = async (
    finalDirection: 1 | -1 | 0,
    previousState: VoteState
  ) => {
    loading.value = true
    try {
      const body: any = {
        direction: finalDirection
      }
      body[targetType + '_id'] = targetId

      const response = await client.POST('/v1/vote', { body })

      if (response.error) {
        throw new Error(response.error.message || '投票失败')
      }

      // 可选：同步后端返回的精确值
      // if (response.data) {
      //   // 使用后端返回的精确计数
      // }
    } catch (error: any) {
      // 失败时回滚状态（确保回滚时也是非负数）
      internalState.value = {
        upvotes: Math.max(0, previousState.upvotes),
        downvotes: Math.max(0, previousState.downvotes),
        userVote: previousState.userVote
      }
      console.error('投票失败:', error)
      // 只在非取消操作时显示错误提示
      if (finalDirection !== 0) {
        ElMessage.warning({
          message: error.message || '操作失败，请重试',
          duration: 2000
        })
      }
    } finally {
      loading.value = false
    }
  }

  /**
   * 刷新投票状态
   */
  const refreshVoteStatus = async () => {
    loading.value = true
    try {
      const endpoint = targetType === 'post'
        ? '/v1/posts/{post_id}/vote'
        : '/v1/comments/{comment_id}/vote'

      const response = await client.GET(endpoint, {
        params: {
          path: { [targetType + '_id']: targetId }
        }
      })

      if (response.data) {
        // 从后端刷新状态时，也确保非负数
        internalState.value = {
          upvotes: Math.max(0, response.data.upvotes),
          downvotes: Math.max(0, response.data.downvotes),
          userVote: response.data.user_vote
        }
      }
    } catch (error) {
      console.error('刷新投票状态失败:', error)
    } finally {
      loading.value = false
    }
  }

  /**
   * 组件卸载时清理定时器
   * 如果有待发送的状态，立即发送
   */
  const cleanup = () => {
    if (debounceTimer && pendingDirection.value !== null) {
      clearTimeout(debounceTimer)
      // 立即发送待处理请求
      sendVoteToBackend(pendingDirection.value, rollbackState.value || internalState.value)
      debounceTimer = null
    }
  }

  // 组件卸载时自动清理
  onUnmounted(() => {
    cleanup()
  })

  // 返回响应式状态和方法
  return {
    // 状态
    state: computed(() => internalState.value),
    loading,
    pendingDirection,
    // 计算属性 - 使用 Math.max(0, value) 确保永远不显示负数
    upvotes: computed(() => Math.max(0, internalState.value.upvotes)),
    downvotes: computed(() => Math.max(0, internalState.value.downvotes)),
    userVote: computed(() => internalState.value.userVote),
    score: computed(() => Math.max(0, internalState.value.upvotes) - Math.max(0, internalState.value.downvotes)),
    // 方法
    handleVote,
    refreshVoteStatus,
    cleanup
  }
}
