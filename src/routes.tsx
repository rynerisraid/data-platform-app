import { lazy } from "react";

// Layouts
import { DashboardLayout } from "@/components/dashboard/dashboard-layout";

// Pages
const DashboardMain = lazy(() => import("@/pages/dashboard/main"));
const Analytics = lazy(() => import("@/pages/dashboard/analytics"));
const Projects = lazy(() => import("@/pages/dashboard/projects"));
const ResourcesPage = lazy(() => import("@/pages/dashboard/resources"));
const Team = lazy(() => import("@/pages/dashboard/team"));
const Lifecycle = lazy(() => import("@/pages/dashboard/lifecycle"));
const Settings = lazy(() => import("@/pages/dashboard/settings"));
const About = lazy(() => import("@/pages/about"));
const Home = lazy(() => import("@/pages/index"));
const Analysis = lazy(() => import("@/pages/analysis/index"));
const NotFound = lazy(() => import("@/pages/404"));

//login and register
const LoginPage = lazy(() => import("@/pages/login"));
const RegisterPage = lazy(() => import("@/pages/register"));

const routes = [
  { path: "/login", element: <LoginPage /> },
  { path: "/register", element: <RegisterPage /> },
  { path: "/", element: <Home /> },
  {
    path: "/dashboard",
    element: <DashboardLayout />,
    children: [
      { index: true, element: <DashboardMain /> },
      { path: "analytics", element: <Analytics /> },
      { path: "projects", element: <Projects /> },
      { path: "resources", element: <ResourcesPage /> },
      { path: "team", element: <Team /> },
      { path: "lifecycle", element: <Lifecycle /> },
      { path: "settings", element: <Settings /> },
    ],
  },
  { path: "/about", element: <About /> },
  { path: "/home", element: <Home /> },
  { path: "/analysis", element: <Analysis /> },
  { path: "*", element: <NotFound /> },
];

export default routes;
