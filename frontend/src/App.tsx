import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { DashboardLayout } from './layouts/DashboardLayout';

// Pages
import { Login } from './pages/Login';
import { Register } from './pages/Register';
import { StudentDashboard } from './pages/StudentDashboard';
import { ReportIncident } from './pages/ReportIncident';
import { MyIncidents } from './pages/MyIncidents';
import { IncidentDetails } from './pages/IncidentDetails';
import { AdminDashboard } from './pages/AdminDashboard';
import { AllIncidents } from './pages/AllIncidents';
import { IntelligencePatterns } from './pages/IntelligencePatterns';
import { HotspotAnalysis } from './pages/HotspotAnalysis';
import { RecommendationsPage } from './pages/RecommendationsPage';
import { AssistantChat } from './pages/AssistantChat';
import { TeamsManagement } from './pages/TeamsManagement';
import { SettingsAudit } from './pages/SettingsAudit';

const ProtectedRoute: React.FC<{ children: React.ReactNode; requireAdmin?: boolean }> = ({
  children,
  requireAdmin = false,
}) => {
  const { isAuthenticated, role, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center text-xs text-slate-500">
        Authenticating...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  if (requireAdmin && role !== 'admin') {
    return <Navigate to="/student" replace />;
  }

  return <>{children}</>;
};

const RoleRedirect: React.FC = () => {
  const { isAuthenticated, role, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center text-xs text-slate-500">
        Loading...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <Navigate to={role === 'admin' ? '/admin' : '/student'} replace />;
};

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Authentication routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* Root redirect */}
          <Route path="/" element={<RoleRedirect />} />

          {/* Authenticated Workspace */}
          <Route
            element={
              <ProtectedRoute>
                <DashboardLayout />
              </ProtectedRoute>
            }
          >
            {/* Student & Shared Routes */}
            <Route path="/student" element={<StudentDashboard />} />
            <Route path="/report" element={<ReportIncident />} />
            <Route path="/my-incidents" element={<MyIncidents />} />
            <Route path="/incidents/:id" element={<IncidentDetails />} />

            {/* Administrator Only Routes */}
            <Route
              path="/admin"
              element={
                <ProtectedRoute requireAdmin>
                  <AdminDashboard />
                </ProtectedRoute>
              }
            />
            <Route
              path="/incidents"
              element={
                <ProtectedRoute requireAdmin>
                  <AllIncidents />
                </ProtectedRoute>
              }
            />
            <Route
              path="/intelligence"
              element={
                <ProtectedRoute requireAdmin>
                  <IntelligencePatterns />
                </ProtectedRoute>
              }
            />
            <Route
              path="/hotspots"
              element={
                <ProtectedRoute requireAdmin>
                  <HotspotAnalysis />
                </ProtectedRoute>
              }
            />
            <Route
              path="/recommendations"
              element={
                <ProtectedRoute requireAdmin>
                  <RecommendationsPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/assistant"
              element={
                <ProtectedRoute requireAdmin>
                  <AssistantChat />
                </ProtectedRoute>
              }
            />
            <Route
              path="/teams"
              element={
                <ProtectedRoute requireAdmin>
                  <TeamsManagement />
                </ProtectedRoute>
              }
            />
            <Route
              path="/settings"
              element={
                <ProtectedRoute requireAdmin>
                  <SettingsAudit />
                </ProtectedRoute>
              }
            />
          </Route>

          {/* Fallback */}
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
};

export default App;
