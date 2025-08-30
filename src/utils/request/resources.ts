import instance from "./instance";
import { toast } from "sonner";

// 连接类型枚举
export type ConnectionType = "postgresql" | "mysql" | "mongodb";

export const ConnectionType = {
  POSTGRESQL: "postgresql" as ConnectionType,
  MYSQL: "mysql" as ConnectionType,
  MONGODB: "mongodb" as ConnectionType,
};

// 数据连接创建请求模型
export interface DataConnectionCreate {
  name: string;
  db_type: ConnectionType;
  host: string;
  port: number;
  database: string;
  username: string;
  password: string;
}

// 数据连接测试请求模型
export interface DataConnectionTest {
  db_type: ConnectionType;
  host: string;
  port: number;
  database?: string;
  username: string;
  password: string;
}

// 数据连接测试响应模型
export interface DataConnectionTestResponse {
  success: boolean;
  error?: string;
  message?: string;
}

// 数据连接读取模型
export interface DataConnectionRead {
  id: string;
  name: string;
  db_type: ConnectionType;
  host: string;
  port?: number;
  database?: string;
  username?: string;
}

// 测试数据连接
export async function testDataConnection(
  connectionConfig: DataConnectionTest
): Promise<DataConnectionTestResponse> {
  try {
    const response = await instance.post<DataConnectionTestResponse>(
      "/resources/connectors/test/",
      connectionConfig
    );
    return response.data;
  } catch (error: any) {
    toast.error(error.message || "Failed to test connection");
    throw error;
  }
}

// 创建数据连接
export async function createDataConnection(
  dataConnection: DataConnectionCreate
): Promise<DataConnectionRead> {
  console.log("createDataConnection", dataConnection);
  try {
    const response = await instance.post<DataConnectionRead>(
      "/resources/connectors/",
      dataConnection
    );
    toast.success("Data connection created successfully");
    return response.data;
  } catch (error: any) {
    toast.error(error.message || "Failed to create data connection");
    throw error;
  }
}

// 获取数据连接列表
export async function getDataConnections(
  skip: number = 0,
  limit: number = 100
): Promise<DataConnectionRead[]> {
  try {
    const response = await instance.get<DataConnectionRead[]>(
      "/resources/connectors/",
      {
        params: { skip, limit },
      }
    );
    return response.data;
  } catch (error: any) {
    toast.error(error.message || "Failed to fetch data connections");
    throw error;
  }
}

// 获取单个数据连接
export async function getDataConnection(
  connectionId: string
): Promise<DataConnectionRead> {
  try {
    const response = await instance.get<DataConnectionRead>(
      `/resources/connectors/${connectionId}`
    );
    return response.data;
  } catch (error: any) {
    toast.error(error.message || "Failed to fetch data connection");
    throw error;
  }
}

// 更新数据连接
export async function updateDataConnection(
  connectionId: string,
  dataConnection: Partial<DataConnectionCreate>
): Promise<DataConnectionRead> {
  try {
    const response = await instance.put<DataConnectionRead>(
      `/resources/connectors/${connectionId}`,
      dataConnection
    );
    toast.success("Data connection updated successfully");
    return response.data;
  } catch (error: any) {
    toast.error(error.message || "Failed to update data connection");
    throw error;
  }
}

// 删除数据连接
export async function deleteDataConnection(
  connectionId: string
): Promise<void> {
  try {
    await instance.delete(`/resources/connectors/${connectionId}`);
    toast.success("Data connection deleted successfully");
  } catch (error: any) {
    toast.error(error.message || "Failed to delete data connection");
    throw error;
  }
}
