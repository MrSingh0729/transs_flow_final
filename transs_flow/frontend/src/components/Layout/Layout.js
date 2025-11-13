import React from "react";
import Sidebar from "./Sidebar";

const Layout = ({ children }) => {
  return (
    <div className="flex min-h-screen">
      {/* Sidebar (hidden on mobile) */}
      <Sidebar />

      {/* Main content */}
      <main className="flex-1 md:ml-64 bg-gray-50 min-h-screen p-4 sm:p-6">
        {children}
      </main>
    </div>
  );
};

export default Layout;
