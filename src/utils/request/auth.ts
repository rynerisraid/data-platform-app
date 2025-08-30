import instance from "./instance";

export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  // 根据你的 UserRead 模型添加其他字段
}

// 登录
export async function login(credentials: LoginRequest): Promise<TokenResponse> {
  const params = new URLSearchParams();
  params.append("username", credentials.username);
  params.append("password", credentials.password);

  const response = await instance.post<TokenResponse>(
    "/auth/front_token",
    params,
    {
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
    }
  );
  // 保存token到localStorage
  if (response.data.access_token) {
    localStorage.setItem("access_token", response.data.access_token);
  }

  return response.data;
}

// 获取当前用户信息
export async function getCurrentUser(): Promise<User> {
  const response = await instance.get<User>("/auth/me");
  return response.data;
}

// 登出
export function logout(): void {
  localStorage.removeItem("access_token");
}

// 检查是否已登录
export function isAuthenticated(): boolean {
  return !!localStorage.getItem("access_token");
}
