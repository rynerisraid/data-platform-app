import axios from "axios";
import { toast } from "sonner";

const instance = axios.create({
  baseURL: import.meta.env.VITE_BACKEND_URL || "http://localhost:8000",
  timeout: 5000,
});
// 请求拦截器
instance.interceptors.request.use(
  (config) => {
    // 在发送请求之前做些什么
    //const access_token ="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkZXZAZXhhbXBsZS5jb20iLCJleHAiOjE3NTY0Mzg0NzB9.cnF26suaqzWh96T7aRdGNkiTnEXJ2c3BmwLRsMRVibQ";
    const token = localStorage.getItem("access_token"); // access_token; //

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    // 对请求错误做些什么
    return Promise.reject(error);
  }
);

// 响应拦截器
instance.interceptors.response.use(
  (response) => {
    // 2xx 范围内的状态码都会触发该函数
    // 对响应数据做点什么
    return response.data;
  },
  (error) => {
    // 超出 2xx 范围的状态码都会触发该函数
    // 对响应错误做点什么
    console.log(error);
    // 处理特定的错误状态码
    if (error.response?.status === 401) {
      // 未授权，清除本地token并跳转到登录页
      localStorage.removeItem("access_token");
      toast.error("登录已过期，请重新登录");
      // 可以在这里添加跳转到登录页的逻辑
      window.location.href = "/login";
    } else {
      toast.error(error.response?.data?.detail || error.message);
    }
    return Promise.reject(error);
  }
);

export default instance;
