import React from "react";
import Sidebar from "./Sidebar";
import BottomNav from "./BottomNav";

const MainLayout = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      {/* Sidebar for desktop */}
      <div className="flex flex-1">
        <Sidebar />
        <main className="flex-1 md:ml-64 p-3 sm:p-5 overflow-y-auto">
          {children}
        </main>
      </div>

      {/* Bottom navigation for mobile */}
      <BottomNav />
    </div>
  );
};

export default MainLayout;
