'use client';

import { useEffect } from 'react';
import { useSearchParams } from 'next/navigation';

export default function AuthCallback() {
  const searchParams = useSearchParams();

  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      localStorage.setItem('coinmatch_token', token);
      window.location.href = '/dashboard';
    } else {
      window.location.href = '/auth/login?error=oauth_failed';
    }
  }, [searchParams]);

  return (
    <main className="min-h-screen bg-navy-500 flex items-center justify-center">
      <div className="text-center">
        <span className="text-5xl">🪙</span>
        <p className="text-gold-400 mt-4 text-xl">Logging you in...</p>
      </div>
    </main>
  );
}
