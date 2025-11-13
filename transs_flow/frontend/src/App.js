import React, { Suspense } from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import { ToastContainer } from "react-toastify";
import { useAuth } from "./contexts/AuthContext";
import { Helmet } from "react-helmet-async";
import LoadingSpinner from "./components/LoadingSpinner";
import ProtectedRoute from "./components/ProtectedRoute";
import OfflineBanner from "./components/OfflineBanner";
import MainLayout from "./components/Layout/MainLayout"; // 🆕 layout wrapper

// ===== Lazy load pages =====
const Login = React.lazy(() => import("./pages/Login"));
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const WorkInfoForm = React.lazy(() => import("./pages/WorkInfoForm"));
const FAITestForm = React.lazy(() => import("./pages/FAITestForm"));
const AuditForm = React.lazy(() => import("./pages/AuditForm"));
const BTBForm = React.lazy(() => import("./pages/BTBForm"));
const DisassembleForm = React.lazy(() => import("./pages/DisassembleForm"));
const NCIssueForm = React.lazy(() => import("./pages/NCIssueForm"));
const ESDForm = React.lazy(() => import("./pages/ESDForm"));
const OperatorQualForm = React.lazy(() => import("./pages/OperatorQualForm"));
const DustCountForm = React.lazy(() => import("./pages/DustCountForm"));
const DynamicFormPage = React.lazy(() => import("./pages/DynamicFormPage"));
const ScannerPage = React.lazy(() => import("./pages/ScannerPage"));
const CameraPage = React.lazy(() => import("./pages/CameraPage"));
const Settings = React.lazy(() => import("./pages/Settings"));

function App() {
  const { user, loading } = useAuth();

  if (loading) {
    return <LoadingSpinner />;
  }

  return (
    <>
      <Helmet>
        <title>Transs Flow - IPQC Inspector</title>
        <meta name="description" content="IPQC Quality Inspection App" />
        <link rel="manifest" href="/manifest.json" />
        <meta name="theme-color" content="#0ea5e9" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="Transs Flow" />
        <link rel="apple-touch-icon" href="/logo192.png" />
      </Helmet>

      <OfflineBanner />

      <Suspense fallback={<LoadingSpinner />}>
        <Routes>
          {/* === Public Routes === */}
          <Route path="/login" element={!user ? <Login /> : <Navigate to="/" />} />

          {/* === Protected Routes (Wrapped in MainLayout) === */}
          <Route
            path="/"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <Dashboard />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/workinfo"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <WorkInfoForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/fai"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <FAITestForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/audit"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <AuditForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/btb"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <BTBForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/disassemble"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <DisassembleForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/nc-issue"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <NCIssueForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/esd"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <ESDForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/operator-qual"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <OperatorQualForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dust-count"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <DustCountForm />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/dynamic-form/:formId"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <DynamicFormPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/scanner"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <ScannerPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/camera"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <CameraPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          <Route
            path="/settings"
            element={
              <ProtectedRoute user={user}>
                <MainLayout>
                  <Settings />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          {/* === Redirects === */}
          <Route
            path="*"
            element={user ? <Navigate to="/" /> : <Navigate to="/login" />}
          />
        </Routes>
      </Suspense>

      <ToastContainer
        position="bottom-right"
        autoClose={3000}
        hideProgressBar={false}
        newestOnTop={false}
        closeOnClick
        pauseOnHover
        theme="light"
      />
    </>
  );
}

export default App;
