"use client";

import { ElMessage } from "element-plus";
import type { Middleware } from "openapi-fetch";
import createFetchClient from "openapi-fetch";
import type { paths } from "./schema";

const createInterceptor = (): Middleware => {
  return {
    async onResponse({ response }) {
      const { status } = response;

      // 错误处理
      if (status === 0) {
        ElMessage.error("网络连接失败，请检查网络连接");
        return response;
      }

      if (status >= 400) {
        try {
          const body = await response.clone().json();
          if (body?.detail) {
            ElMessage.error(body.detail);
          }
        } catch (e) {
          // JSON 解析失败，忽略
        }

        if (status === 408) {
          ElMessage.error("请求超时，请稍后重试");
        }
        return response;
      }

      // 成功处理
      if (status >= 200 && status < 300) {
        try {
          const body = await response.clone().json();
          if (body?.message) {
            ElMessage.success(body.message);
          }
        } catch (e) {
          // JSON 解析失败，忽略
        }
      }

      return response;
    },

    async onRequest({ request }) {
      try {
        const tokenStr = localStorage.getItem("token");
        if (tokenStr) {
          const token = JSON.parse(tokenStr);
          if (token && token !== "") {
            request.headers.set("Authorization", `Bearer ${token}`);
          }
        }
      } catch (error) {
        console.error("Failed to parse token from localStorage:", error);
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

// 只导出 client，移除未使用的导出
export { client };
