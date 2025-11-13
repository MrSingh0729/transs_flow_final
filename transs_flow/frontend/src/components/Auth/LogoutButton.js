import React from 'react';
import { useAuth } from './useAuth';

export default function LogoutButton() {
  const { logout } = useAuth();
  return (
    <button onClick={logout} className="bg-red-600 text-white px-3 py-1 rounded-lg">
      Logout
    </button>
  );
}
