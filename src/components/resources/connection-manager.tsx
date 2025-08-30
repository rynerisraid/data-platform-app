import React, { useState, useEffect } from "react";
import { toast } from "sonner";
import {
  ConnectionType,
  type DataConnectionCreate,
  type DataConnectionRead,
  type DataConnectionTest,
  createDataConnection,
  deleteDataConnection,
  getDataConnections,
  testDataConnection,
  updateDataConnection,
} from "@/utils/request/resources";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import {
  IconPlus,
  IconTrash,
  IconPencil,
  IconTestPipe,
} from "@tabler/icons-react";

export function ConnectionManager() {
  const [connections, setConnections] = useState<DataConnectionRead[]>([]);
  const [loading, setLoading] = useState(true);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [editingConnection, setEditingConnection] =
    useState<DataConnectionRead | null>(null);
  const [formData, setFormData] = useState<
    Omit<DataConnectionCreate, "name"> & { name: string }
  >({
    name: "",
    db_type: ConnectionType.POSTGRESQL,
    host: "",
    port: 5432,
    database: "",
    username: "",
    password: "",
  });

  useEffect(() => {
    fetchConnections();
  }, []);

  const fetchConnections = async () => {
    try {
      setLoading(true);
      const data = await getDataConnections();
      setConnections(data);
    } catch (error) {
      console.error("Failed to fetch connections:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: name === "port" ? parseInt(value) || 0 : value,
    }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    try {
      if (editingConnection) {
        // 更新连接
        await updateDataConnection(editingConnection.id, formData);
      } else {
        // 创建新连接
        await createDataConnection(formData as DataConnectionCreate);
      }

      // 重置表单和状态
      resetForm();
      await fetchConnections();
    } catch (error) {
      console.error("Failed to save connection:", error);
    }
  };

  const handleEdit = (connection: DataConnectionRead) => {
    setEditingConnection(connection);
    setFormData({
      name: connection.name,
      db_type: connection.db_type,
      host: connection.host,
      port:
        connection.port ||
        (connection.db_type === ConnectionType.POSTGRESQL ? 5432 : 3306),
      database: connection.database || "",
      username: connection.username || "",
      password: "", // 不从服务器获取密码
    });
    setIsDialogOpen(true);
  };

  const handleDelete = async (id: string) => {
    if (window.confirm("Are you sure you want to delete this connection?")) {
      try {
        await deleteDataConnection(id);
        await fetchConnections();
      } catch (error) {
        console.error("Failed to delete connection:", error);
      }
    }
  };

  const handleTestConnection = async () => {
    try {
      const testConfig: DataConnectionTest = {
        db_type: formData.db_type,
        host: formData.host,
        port: formData.port,
        database: formData.database,
        username: formData.username,
        password: formData.password,
      };

      const response = await testDataConnection(testConfig);
      if (response.success) {
        toast.success("Connection test successful! Database is accessible.");
      } else {
        toast.error(
          `Connection test failed: ${response.error || "Unknown error"}`
        );
      }
    } catch (error) {
      toast.error("Failed to test connection");
      console.error("Failed to test connection:", error);
    }
  };

  const resetForm = () => {
    setFormData({
      name: "",
      db_type: ConnectionType.POSTGRESQL,
      host: "",
      port: 5432,
      database: "",
      username: "",
      password: "",
    });
    setEditingConnection(null);
    setIsDialogOpen(false);
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Data Connections</h2>
        <Dialog
          open={isDialogOpen}
          onOpenChange={(open) => {
            setIsDialogOpen(open);
            if (!open) resetForm();
          }}>
          <DialogTrigger asChild>
            <Button onClick={() => setIsDialogOpen(true)}>
              <IconPlus className="mr-2 h-4 w-4" />
              Add Connection
            </Button>
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>
                {editingConnection ? "Edit Connection" : "Add New Connection"}
              </DialogTitle>
              <DialogDescription>
                {editingConnection
                  ? "Edit the connection details below"
                  : "Enter the details for your new data connection"}
              </DialogDescription>
            </DialogHeader>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 gap-2">
                <div className="space-y-2">
                  <Label htmlFor="db_type">Database Type</Label>
                  <Select
                    value={formData.db_type}
                    onValueChange={(value) =>
                      handleSelectChange("db_type", value)
                    }>
                    <SelectTrigger>
                      <SelectValue placeholder="Select database type" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value={ConnectionType.POSTGRESQL}>
                        PostgreSQL
                      </SelectItem>
                      <SelectItem value={ConnectionType.MYSQL}>
                        MySQL
                      </SelectItem>
                      <SelectItem value={ConnectionType.MONGODB}>
                        MongoDB
                      </SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2 col-span-3">
                  <Label htmlFor="name">Name</Label>
                  <Input
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>
              <div className="grid grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="host">Host</Label>
                  <Input
                    id="host"
                    name="host"
                    value={formData.host}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="port">Port</Label>
                  <Input
                    id="port"
                    name="port"
                    type="number"
                    value={formData.port}
                    onChange={handleInputChange}
                    required
                  />
                </div>

                <div className="space-y-2">
                  <Label htmlFor="database">Database</Label>
                  <Input
                    id="database"
                    name="database"
                    value={formData.database}
                    onChange={handleInputChange}
                    required
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="username">Username</Label>
                <Input
                  id="username"
                  name="username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input
                  id="password"
                  name="password"
                  type="password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required={!editingConnection} // 编辑时密码可选
                />
              </div>

              <DialogFooter className="gap-2">
                <Button
                  type="button"
                  variant="outline"
                  onClick={handleTestConnection}>
                  <IconTestPipe className="mr-2 h-4 w-4" />
                  Test Connection
                </Button>
                <Button type="button" variant="outline" onClick={resetForm}>
                  Cancel
                </Button>
                <Button type="submit">
                  {editingConnection ? "Update" : "Create"}
                </Button>
              </DialogFooter>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {loading ? (
        <div>Loading connections...</div>
      ) : (
        <div className="border rounded-lg">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Type</TableHead>
                <TableHead>Host</TableHead>
                <TableHead>Port</TableHead>
                <TableHead>Database</TableHead>
                <TableHead>Username</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {connections &&
                connections.map((connection) => (
                  <TableRow key={connection.id}>
                    <TableCell className="font-medium">
                      {connection.name}
                    </TableCell>
                    <TableCell>{connection.db_type}</TableCell>
                    <TableCell>{connection.host}</TableCell>
                    <TableCell>{connection.port}</TableCell>
                    <TableCell>{connection.database}</TableCell>
                    <TableCell>{connection.username}</TableCell>
                    <TableCell className="text-right">
                      <div className="flex justify-end gap-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleEdit(connection)}>
                          <IconPencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => handleDelete(connection.id)}>
                          <IconTrash className="h-4 w-4" />
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              {connections && connections.length === 0 && (
                <TableRow>
                  <TableCell
                    colSpan={7}
                    className="text-center py-8 text-muted-foreground">
                    No data connections found. Create your first connection.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}
