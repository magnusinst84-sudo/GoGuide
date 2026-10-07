'use client';

import { useState } from 'react';
import { checkHealth } from '@/lib/api';

export default function Home() {
  const [status, setStatus] = useState<string>('');

  const handleHealthCheck = async () => {
    try {
      const res = await checkHealth();
      setStatus(JSON.stringify(res, null, 2));
    } catch (e) {
      setStatus('Failed to connect to backend.');
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-8">
      <h1 className="text-4xl font-bold text-blue-600 mb-4">GoGuide</h1>
      <p className="text-xl mb-8">AI-powered education and career guidance for students and families.</p>
      
      <button 
        onClick={handleHealthCheck}
        className="px-6 py-3 bg-blue-600 text-white rounded shadow hover:bg-blue-700 transition"
      >
        Check Backend Health
      </button>

      {status && (
        <pre className="mt-8 p-4 bg-gray-800 text-green-400 rounded w-full max-w-xl overflow-auto text-sm">
          {status}
        </pre>
      )}
    </main>
  );
}
