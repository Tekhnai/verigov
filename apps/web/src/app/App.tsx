import { Navigate, Route, Routes } from "react-router-dom";

import LoginPage from "../features/auth/LoginPage";
import DashboardPage from "../features/dashboard/DashboardPage";
import TargetsPage from "../features/targets/TargetsPage";
import TargetDetailPage from "../features/targets/TargetDetailPage";
import AppLayout from "../components/AppLayout";
import RequireAuth from "./RequireAuth";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<RequireAuth />}>
        <Route element={<AppLayout />}>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/targets" element={<TargetsPage />} />
          <Route path="/targets/:id" element={<TargetDetailPage />} />
        </Route>
      </Route>
      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
