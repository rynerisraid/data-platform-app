import { Suspense } from "react";
import { useRoutes, Navigate } from "react-router-dom";
import routes from "@/routes";

export default function App() {
  const router = useRoutes([
    ...routes,
    { path: "/", element: <Navigate to="/dashboard" /> },
  ]);

  return <Suspense fallback={<p>Loading...</p>}>{router}</Suspense>;
}
