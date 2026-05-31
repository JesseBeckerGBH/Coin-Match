'use client';

import { useEffect, useState } from 'react';
import { getMe, getDashboardStats } from '@/lib/api';
import Link from 'next/link';

interface User {
  id: string;
  name: string;
  email: string;
  user_type: string;
  tier: string;
  role: string;
  total_purchases: number;
  total_sales: number;
}

interface Stats {
  user_type: string;
  tier: string;
  total_purchases: number;
  total_sales: number;
  active_wants?: number;
  pending_matches?: number;
  active_listings?: number;
  coins_sold?: number;
}

export default function Dashboard() {
  const [user, setUser] = useState<User | null>(null);
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('coinmatch_token');
    if (!token) {
      window.location.href = '/auth/login';
      return;
    }

    Promise.all([getMe(), getDashboardStats()])
      .then(([userRes, statsRes]) => {
        setUser(userRes.data);
        setStats(statsRes.data);
      })
      .catch(() => {
        localStorage.removeItem('coinmatch_token');
        window.location.href = '/auth/login';
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center py-32">
        <span className="text-4xl animate-pulse">🪙</span>
      </div>
    );
  }

  if (!user || !stats) return null;

  const isSeller = ['active_seller', 'estate_seller', 'dealer'].includes(
    user.user_type
  );
  const isBuyer = ['buyer', 'dealer'].includes(user.user_type);

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Welcome */}
      <h1 className="text-3xl font-bold text-navy-500 mb-2">
        Welcome back, {user.name.split(' ')[0]} 👋
      </h1>
      <p className="text-navy-300 mb-8">
        {user.user_type === 'estate_seller'
          ? 'Upload your coin photos to get started with a free AI assessment.'
          : "Here's your marketplace activity at a glance."}
      </p>

      {/* Stats grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        {isBuyer && (
          <>
            <StatCard
              label="Active Wants"
              value={stats.active_wants ?? 0}
              icon="🔍"
            />
            <StatCard
              label="Pending Matches"
              value={stats.pending_matches ?? 0}
              icon="🎯"
            />
            <StatCard
              label="Total Purchases"
              value={stats.total_purchases}
              icon="🛒"
            />
          </>
        )}
        {isSeller && (
          <>
            <StatCard
              label="Active Listings"
              value={stats.active_listings ?? 0}
              icon="📋"
            />
            <StatCard
              label="Coins Sold"
              value={stats.coins_sold ?? 0}
              icon="✅"
            />
            <StatCard
              label="Total Sales"
              value={stats.total_sales}
              icon="💰"
            />
          </>
        )}
        <StatCard
          label="Tier"
          value={stats.tier.charAt(0).toUpperCase() + stats.tier.slice(1)}
          icon="⭐"
          isText
        />
      </div>

      {/* Quick actions */}
      <div className="grid md:grid-cols-2 gap-6">
        {isSeller && (
          <div className="card">
            <h2 className="text-xl font-bold text-navy-500 mb-3">
              📸 List a Coin
            </h2>
            <p className="text-navy-300 mb-4">
              Upload photos of your coin. Our AI will grade it instantly and
              match it with interested buyers.
            </p>
            <Link
              href="/dashboard/sell"
              className="btn-primary inline-block text-sm"
            >
              Start Listing →
            </Link>
          </div>
        )}

        {isBuyer && (
          <div className="card">
            <h2 className="text-xl font-bold text-navy-500 mb-3">
              🔍 Want List
            </h2>
            <p className="text-navy-300 mb-4">
              Tell us what you&apos;re looking for. We&apos;ll notify you the
              moment a matching coin hits the marketplace.
            </p>
            <Link
              href="/dashboard/wants"
              className="btn-primary inline-block text-sm"
            >
              Manage Want List →
            </Link>
          </div>
        )}

        <div className="card">
          <h2 className="text-xl font-bold text-navy-500 mb-3">
            🪙 Fresh Estate Inventory
          </h2>
          <p className="text-navy-300 mb-4">
            Browse coins from estate sellers — often underpriced and available
            before they hit the public market.
            {user.tier === 'free' && ' Upgrade to Pro for 24h early access.'}
          </p>
          <Link
            href="/dashboard/fresh"
            className="btn-secondary inline-block text-sm"
          >
            Browse Estate Coins →
          </Link>
        </div>

        <div className="card">
          <h2 className="text-xl font-bold text-navy-500 mb-3">
            📊 Browse Marketplace
          </h2>
          <p className="text-navy-300 mb-4">
            Search all listed coins by type, grade, year, mint mark, and price.
          </p>
          <Link
            href="/dashboard/browse"
            className="btn-secondary inline-block text-sm"
          >
            Browse All Coins →
          </Link>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  label,
  value,
  icon,
  isText = false,
}: {
  label: string;
  value: number | string;
  icon: string;
  isText?: boolean;
}) {
  return (
    <div className="card text-center">
      <div className="text-2xl mb-1">{icon}</div>
      <p
        className={`font-bold text-navy-500 ${isText ? 'text-lg' : 'text-3xl'}`}
      >
        {value}
      </p>
      <p className="text-sm text-navy-300">{label}</p>
    </div>
  );
}
