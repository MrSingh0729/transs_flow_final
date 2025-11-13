import React from "react";
import { NavLink } from "react-router-dom";

const Sidebar = () => {
  return (
    <aside className="hidden md:flex flex-col w-64 bg-white border-r border-gray-200 fixed h-full left-0 top-0 z-40">
      <div className="flex items-center justify-center h-16 border-b">
        <h1 className="text-sky-600 font-bold text-xl">Transs Flow</h1>
      </div>

      <nav className="flex-1 overflow-y-auto p-3">
        <ul className="space-y-1">
          <li>
            <NavLink
              to="/"
              className={({ isActive }) =>
                `flex items-center gap-3 p-2 rounded-lg hover:bg-sky-50 ${
                  isActive ? "bg-sky-100 text-sky-600 font-semibold" : "text-gray-700"
                }`
              }
            >
              <i className="fas fa-home"></i> Dashboard
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/workinfo"
              className={({ isActive }) =>
                `flex items-center gap-3 p-2 rounded-lg hover:bg-sky-50 ${
                  isActive ? "bg-sky-100 text-sky-600 font-semibold" : "text-gray-700"
                }`
              }
            >
              <i className="fas fa-clipboard-list"></i> Work Info
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/audit"
              className={({ isActive }) =>
                `flex items-center gap-3 p-2 rounded-lg hover:bg-sky-50 ${
                  isActive ? "bg-sky-100 text-sky-600 font-semibold" : "text-gray-700"
                }`
              }
            >
              <i className="fas fa-search"></i> Assembly Audit
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/operator-qual"
              className={({ isActive }) =>
                `flex items-center gap-3 p-2 rounded-lg hover:bg-sky-50 ${
                  isActive ? "bg-sky-100 text-sky-600 font-semibold" : "text-gray-700"
                }`
              }
            >
              <i className="fas fa-user-check"></i> Operator Qualification
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/nc-issue"
              className={({ isActive }) =>
                `flex items-center gap-3 p-2 rounded-lg hover:bg-sky-50 ${
                  isActive ? "bg-sky-100 text-sky-600 font-semibold" : "text-gray-700"
                }`
              }
            >
              <i className="fas fa-exclamation-triangle"></i> NC Issue
            </NavLink>
          </li>

          <li>
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                `flex items-center gap-3 p-2 rounded-lg hover:bg-sky-50 ${
                  isActive ? "bg-sky-100 text-sky-600 font-semibold" : "text-gray-700"
                }`
              }
            >
              <i className="fas fa-cog"></i> Settings
            </NavLink>
          </li>
        </ul>
      </nav>

      <div className="p-3 border-t">
        <a
          href="/logout"
          className="flex items-center gap-3 p-2 rounded-lg text-red-600 hover:bg-red-50"
        >
          <i className="fas fa-sign-out-alt"></i> Logout
        </a>
      </div>
    </aside>
  );
};

export default Sidebar;
