import { Navigate, useLocation } from "react-router-dom";

import { useAuthStore } from "../stores/authStore";

export function ProtectedRoute({ children }) {
  const token = useAuthStore((state) => state.token);
  const isSetupComplete = useAuthStore((state) => state.isSetupComplete);
  const location = useLocation();

  if (!token) {
    return <Navigate to="/login" replace />;
  }

  if (!isSetupComplete && location.pathname !== "/setup") {
    return <Navigate to="/setup" replace />;
  }

  if (isSetupComplete && location.pathname === "/setup") {
    return <Navigate to="/" replace />;
  }

  return children;
}
