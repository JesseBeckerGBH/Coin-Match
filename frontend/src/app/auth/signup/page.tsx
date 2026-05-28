'use client';

import { useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { signup } from '@/lib/api';

export default function SignupPage() {
  const searchParams = useSearchParams();
  const defaultType = searchParams.get('type') || 'buyer';

  const [form, setForm] = useState({
    email: '',
    password: '',
    name: '',
    user_type: defaultType,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const res = await signup(form);
      localStorage.setItem('coinmatch_token', res.data.access_token);
      window.location.href = '/dashboard';
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Signup failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-navy-500 to-navy-700 flex items-center justify-center px-4">
      <div className="card max-w-md w-full">
        <div className="text-center mb-8">
          <span className="text-4xl">🪙</span>
          <h1 className="text-2xl font-bold text-navy-500 mt-2">Join CoinMatch</h1>
          <p className="text-navy-300 mt-1">
            {defaultType === 'estate_seller'
              ? 'Get a free AI assessment of your coins'
              : 'Start collecting smarter today'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">
              I am a...
            </label>
            <div className="grid grid-cols-3 gap-2">
              {[
                { value: 'buyer', label: '🔍 Collector' },
                { value: 'estate_seller', label: '🏠 Estate Seller' },
                { value: 'dealer', label: '🏪 Dealer' },
              ].map((opt) => (
                <button
                  key={opt.value}
                  type="button"
                  onClick={() => setForm({ ...form, user_type: opt.value })}
                  className={`py-2 px-3 rounded-lg text-sm font-medium border-2 transition-colors ${
                    form.user_type === opt.value
                      ? 'border-gold-400 bg-gold-50 text-navy-500'
                      : 'border-gray-200 text-navy-300 hover:border-gold-200'
                  }`}
                >
                  {opt.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">Name</label>
            <input
              type="text"
              required
              value={form.name}
              onChange={(e) => setForm({ ...form, name: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
              placeholder="Your name"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">Email</label>
            <input
              type="email"
              required
              value={form.email}
              onChange={(e) => setForm({ ...form, email: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
              placeholder="you@example.com"
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">Password</label>
            <input
              type="password"
              required
              minLength={8}
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
              placeholder="Min 8 characters"
            />
          </div>

          {error && (
            <p className="text-red-500 text-sm">{error}</p>
          )}

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full disabled:opacity-50"
          >
            {loading ? 'Creating account...' : 'Create Account'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <div className="relative my-4">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-navy-300">or</span>
            </div>
          </div>
          <a
            href={`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/auth/oauth/google`}
            className="flex items-center justify-center gap-2 w-full py-2 px-4 border-2 border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92a5.06 5.06 0 0 1-2.2 3.32v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.1z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            <span className="text-navy-400 font-medium">Continue with Google</span>
          </a>
        </div>

        <p className="text-center text-sm text-navy-300 mt-6">
          Already have an account?{' '}
          <a href="/auth/login" className="text-gold-500 hover:text-gold-600 font-bold">
            Log in
          </a>
        </p>
      </div>
    </main>
  );
}
