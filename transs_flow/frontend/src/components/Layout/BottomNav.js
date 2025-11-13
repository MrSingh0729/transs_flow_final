import React from "react";
import { NavLink } from "react-router-dom";

const BottomNav = () => {
  return (
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 flex justify-around py-2 z-50 md:hidden">
      <NavLink
        to="/"
        className={({ isActive }) =>
          `flex flex-col items-center text-xs ${
            isActive ? "text-sky-600" : "text-gray-500"
          }`
        }
      >
        <i className="fas fa-home text-lg"></i>
        Home
      </NavLink>

      <NavLink
        to="/workinfo"
        className={({ isActive }) =>
          `flex flex-col items-center text-xs ${
            isActive ? "text-sky-600" : "text-gray-500"
          }`
        }
      >
        <i className="fas fa-clipboard-list text-lg"></i>
        Work
      </NavLink>

      <NavLink
        to="/audit"
        className={({ isActive }) =>
          `flex flex-col items-center text-xs ${
            isActive ? "text-sky-600" : "text-gray-500"
          }`
        }
      >
        <i className="fas fa-search text-lg"></i>
        Audit
      </NavLink>

      <NavLink
        to="/nc-issue"
        className={({ isActive }) =>
          `flex flex-col items-center text-xs ${
            isActive ? "text-sky-600" : "text-gray-500"
          }`
        }
      >
        <i className="fas fa-exclamation-triangle text-lg"></i>
        Issues
      </NavLink>

      <NavLink
        to="/settings"
        className={({ isActive }) =>
          `flex flex-col items-center text-xs ${
            isActive ? "text-sky-600" : "text-gray-500"
          }`
        }
      >
        <i className="fas fa-user text-lg"></i>
        Profile
      </NavLink>
    </nav>
  );
};

export default BottomNav;
