import React, { useState } from 'react';
import { useAuth } from './useAuth';

export default function LoginForm() {
  const { login } = useAuth();
  const [employee_id, setEmployeeId] = useState('');
  const [password, setPassword] = useState('');

  const handleSubmit = async e => {
    e.preventDefault();
    await login(employee_id, password);
  };

  return (
    <form onSubmit={handleSubmit} className="p-6 space-y-4 bg-white rounded-xl shadow-md">
      <input type="text" value={employee_id} onChange={e => setEmployeeId(e.target.value)} placeholder="Employee ID" className="border p-2 w-full rounded-md" />
      <input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" className="border p-2 w-full rounded-md" />
      <button type="submit" className="bg-blue-600 text-white w-full py-2 rounded-md hover:bg-blue-700">Login</button>
    </form>
  );
}
