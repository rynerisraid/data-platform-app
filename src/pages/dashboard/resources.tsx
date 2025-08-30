import { useEffect } from "react";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import MetaDataTable from "@/components/resources/meta-data-table";
//import Connections from "@/components/resources/connections";
import ComputeNode from "@/components/resources/compute-node";
import { ConnectionManager } from "@/components/resources/connection-manager";

export default function ResourcesPage() {
  useEffect(() => {}, []);
  return (
    <Tabs defaultValue="meta_data_table" className="w-[400px] w-full">
      <TabsList>
        <TabsTrigger value="meta_data_table">数据表格</TabsTrigger>
        <TabsTrigger value="data_connection">数据连接器</TabsTrigger>
        <TabsTrigger value="compute_node">计算节点</TabsTrigger>
      </TabsList>
      <TabsContent value="meta_data_table">
        <MetaDataTable />
      </TabsContent>
      <TabsContent value="data_connection">
        <ConnectionManager />
      </TabsContent>
      <TabsContent value="compute_node">
        <ComputeNode />
      </TabsContent>
    </Tabs>
  );
}
