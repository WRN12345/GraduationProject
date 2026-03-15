"use client";

import { ElMessage } from "element-plus";
import type { Middleware } from "openapi-fetch";
import createFetchClient from "openapi-fetch";
import type { paths } from "./schema";

// Token 刷新状态管理
let isRefreshing = false;
let refreshSubscribers: Array<(token: string) => void> = [];

const addRefreshSubscriber = (callback: (token: string) => void) => {
  refreshSubscribers.push(callback);
};

const onRefreshed = (token: string) => {
  refreshSubscribers.forEach((callback) => callback(token));
  refreshSubscribers = [];
};

const createInterceptor = (): Middleware => {
  return {
    async onResponse({ response }) {
      const { status } = response;
      const url = response.url;

      console.log(`[API Client] 响应: ${status} ${url}`);

      // 网络错误处理
      if (status === 0) {
        console.error('[API Client] 网络连接失败');
        ElMessage.error("网络连接失败，请检查网络连接");
        return response;
      }

      // Token 过期处理
      if (status === 401) {
        console.log('[API Client] Token 过期，尝试刷新');

        // 只在非登录页面才尝试刷新 token
        if (window.location.pathname !== '/login') {
          // 动态导入 userStore 避免循环依赖
          const { useUserStore } = await import("@/stores/user");
          const userStore = useUserStore();

          if (!isRefreshing) {
            isRefreshing = true;

            try {
              // 尝试刷新 token
              const success = await userStore.refreshAccessToken();

              if (success && userStore.token) {
                // 刷新成功，通知所有等待的请求
                onRefreshed(userStore.token);

                // 返回原始 401 响应，让应用层处理重试
                return response;
              } else {
                // 刷新失败，清除认证并跳转登录
                userStore.clearAuth();
                window.location.href = "/login";
                return response;
              }
            } catch (error) {
              // 刷新过程出错
              console.error("Token refresh failed:", error);
              userStore.clearAuth();
              window.location.href = "/login";
              return response;
            } finally {
              isRefreshing = false;
            }
          } else {
            // 正在刷新，等待刷新完成
            return new Promise((resolve) => {
              addRefreshSubscriber((token) => {
                const newHeaders = new Headers();
                response.headers.forEach((value, key) => {
                  newHeaders.set(key, value);
                });
                newHeaders.set("Authorization", `Bearer ${token}`);

                const newRequest = new Request(response.url, {
                  headers: newHeaders,
                });
                resolve(fetch(newRequest));
              });
            }) as Promise<Response>;
          }
        }
        // 如果是登录页面，不执行 token 刷新逻辑，也不提前返回
        // 让代码继续执行到下面的错误处理逻辑 (status >= 400)
      }

      // 其他错误处理
      if (status >= 400) {
        console.log(`[API Client] 错误响应 ${status}:`, url);
        try {
          const body = await response.clone().json();
          console.log('[API Client] 错误详情:', body);
          if (body?.detail) {
            ElMessage.error(body.detail);
          }
        } catch (e) {
          console.log('[API Client] 无法解析错误响应体');
          // JSON 解析失败，忽略
        }

        if (status === 408) {
          ElMessage.error("请求超时，请稍后重试");
        }
        return response;
      }

      // 成功处理
      if (status >= 200 && status < 300) {
        console.log(`[API Client] 成功响应 ${status}:`, url);

        // 投票和收藏接口使用静默模式（不显示成功提示）
        // 这些操作已有乐观更新 + 视觉反馈，不需要额外的 Toast 提示
        const isSilentEndpoint =
          url.includes('/vote') ||
          url.includes('/bookmark')

        if (!isSilentEndpoint) {
          try {
            const body = await response.clone().json();
            console.log('[API Client] 响应数据:', body);
            if (body?.message) {
              ElMessage.success(body.message);
            }
            if (body?.msg) {
              ElMessage.success(body.msg);
            }
          } catch (e) {
            console.log('[API Client] 响应不是 JSON 格式');
            // JSON 解析失败，忽略
          }
        }
      }

      return response;
    },

    async onRequest({ request }) {
      console.log(`[API Client] 发送请求: ${request.method} ${request.url}`);

      try {
        const tokenStr = localStorage.getItem("token");
        if (tokenStr) {
          const token = JSON.parse(tokenStr);
          if (token && token !== "") {
            request.headers.set("Authorization", `Bearer ${token}`);
            console.log('[API Client] 已添加 Authorization 头');
          }
        }
      } catch (error) {
        console.error("[API Client] Failed to parse token from localStorage:", error);
        if (error instanceof SyntaxError) {
          localStorage.removeItem("token");
        }
      }
    },
  };
};

const client = createFetchClient<paths>({
  baseUrl: "/api",
  credentials: "include",
});

// 注册中间件
client.use(createInterceptor());

export { client };
