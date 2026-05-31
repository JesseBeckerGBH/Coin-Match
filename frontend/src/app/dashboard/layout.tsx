'use client';

import { useEffect, useState } from 'react';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import { getMe } from '@/lib/api';

interface User {
  id: string;
  name: string;
  email: string;
  user_type: string;
  tier: string;
  role: string;
}

const NAV_ITEMS = [
  { href: '/dashboard', label: 'Overview', icon: '📊', exact: true },
  { href: '/dashboard/browse', label: 'Browse', icon: '🔍' },
  { href: '/dashboard/fresh', label: 'Estate Inventory', icon: '🪙' },
  { href: '/dashboard/wants', label: 'Want List', icon: '📋' },
  { href: '/dashboard/sell', label: 'Sell a Coin', icon: '📸' },
];

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = localStorage.getItem('coinmatch_token');
    if (!token) {
      window.location.href = '/auth/login';
      return;
    }
    getMe()
      .then((res) => setUser(res.data))
      .catch(() => {
        localStorage.removeItem('coinmatch_token');
        window.location.href = '/auth/login';
      });
  }, []);

  const isActive = (href: string, exact?: boolean) =>
    exact ? pathname === href : pathname.startsWith(href);

  return (
    <div className="min-h-screen bg-gold-50">
      {/* Top bar */}
      <nav className="bg-navy-500 px-6 py-3 flex items-center justify-between shadow-lg sticky top-0 z-50">
        <div className="flex items-center gap-6">
          <Link href="/dashboard" className="flex items-center gap-2">
            <span className="text-2xl">🪙</span>
            <span className="text-gold-400 text-xl font-bold">CoinMatch</span>
          </Link>
          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive(item.href, item.exact)
                    ? 'bg-gold-400/20 text-gold-400'
                    : 'text-gold-200/70 hover:text-gold-200 hover:bg-white/5'
                }`}
              >
                <span className="mr-1.5">{item.icon}</span>
                {item.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3">
          {user && (
            <>
              <span className="text-gold-200 text-sm hidden sm:inline">
                {user.name}
              </span>
              <span className="bg-gold-400/20 text-gold-400 text-xs font-bold px-2 py-1 rounded">
                {user.tier.toUpperCase()}
              </span>
            </>
          )}
          <button
            onClick={() => {
              localStorage.removeItem('coinmatch_token');
              window.location.href = '/';
            }}
            className="text-gold-200/60 hover:text-gold-200 text-sm"
          >
            Log out
          </button>
        </div>
      </nav>

      {/* Mobile nav */}
      <div className="md:hidden flex overflow-x-auto border-b border-gold-200 bg-white px-2 py-1 gap-1">
        {NAV_ITEMS.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`flex-shrink-0 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
              isActive(item.href, item.exact)
                ? 'bg-gold-400/20 text-navy-500 font-bold'
                : 'text-navy-300 hover:bg-gold-50'
            }`}
          >
            <span className="mr-1">{item.icon}</span>
            {item.label}
          </Link>
        ))}
      </div>

      {/* Page content */}
      <main>{children}</main>
    </div>
  );
}
