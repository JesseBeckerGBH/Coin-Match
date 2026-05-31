'use client';

import { useState, useEffect } from 'react';
import { freshInventory, getMe } from '@/lib/api';
import Link from 'next/link';

interface Coin {
  id: string;
  title: string;
  coin_type: string | null;
  year: number | null;
  mint_mark: string | null;
  ai_grade: string | null;
  ai_grade_numeric: number | null;
  ai_confidence: number | null;
  estimated_value: number | null;
  asking_price: number | null;
  images: Record<string, string> | null;
  is_estate: boolean;
  status: string;
  listed_at: string | null;
}

export default function FreshPage() {
  const [coins, setCoins] = useState<Coin[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [userTier, setUserTier] = useState('free');
  const [selectedCoin, setSelectedCoin] = useState<Coin | null>(null);

  const loadFresh = async (p: number = 1) => {
    setLoading(true);
    try {
      const res = await freshInventory({ page: p, per_page: 12 });
      setCoins(res.data.coins);
      setTotal(res.data.total);
      setPage(p);
    } catch {
      // fallback
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadFresh();
    getMe().then((res) => setUserTier(res.data.tier)).catch(() => {});
  }, []);

  const totalPages = Math.ceil(total / 12);

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-navy-500">
            🪙 Fresh Estate Inventory
          </h1>
          <p className="text-navy-300 mt-1">
            Coins from estate sellers — often underpriced and unique.
            {userTier === 'free'
              ? ' You see listings 24h after they go live.'
              : ' You get early access to new listings!'}
          </p>
        </div>
        {userTier !== 'free' && (
          <span className="bg-gold-400/20 text-gold-600 text-xs font-bold px-3 py-1.5 rounded-lg">
            ⚡ Early Access Active
          </span>
        )}
      </div>

      {userTier === 'free' && (
        <div className="bg-gradient-to-r from-gold-50 to-gold-100 border border-gold-200 rounded-xl px-6 py-4 mb-6 flex items-center justify-between">
          <div>
            <h3 className="font-bold text-navy-500 mb-1">
              ⏰ Free users see estate coins after a 24-hour delay
            </h3>
            <p className="text-sm text-navy-400">
              Pro and Dealer members get instant access to new estate listings.
              The best coins often sell within hours.
            </p>
          </div>
          <Link href="/dashboard" className="btn-primary text-sm flex-shrink-0 ml-4">
            Upgrade to Pro
          </Link>
        </div>
      )}

      {loading ? (
        <div className="text-center py-16">
          <span className="text-4xl animate-pulse">🪙</span>
          <p className="text-navy-300 mt-4">Loading estate inventory...</p>
        </div>
      ) : coins.length === 0 ? (
        <div className="card text-center py-16">
          <span className="text-5xl mb-4 block">🏠</span>
          <h3 className="text-xl font-bold text-navy-500 mb-2">
            No estate coins available right now
          </h3>
          <p className="text-navy-300 mb-6 max-w-md mx-auto">
            Estate listings come in waves. Set up a want list to get notified
            instantly when matching estate coins appear.
          </p>
          <Link href="/dashboard/wants" className="btn-primary inline-block">
            Set Up Want List Alerts →
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {coins.map((coin) => (
              <EstateCard
                key={coin.id}
                coin={coin}
                onClick={() => setSelectedCoin(coin)}
              />
            ))}
          </div>

          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => loadFresh(page - 1)}
                disabled={page <= 1}
                className="px-4 py-2 rounded-lg border border-gray-200 text-sm disabled:opacity-30 hover:bg-gray-50"
              >
                ← Prev
              </button>
              <span className="text-sm text-navy-300 px-4">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => loadFresh(page + 1)}
                disabled={page >= totalPages}
                className="px-4 py-2 rounded-lg border border-gray-200 text-sm disabled:opacity-30 hover:bg-gray-50"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {selectedCoin && (
        <EstateCoinModal
          coin={selectedCoin}
          onClose={() => setSelectedCoin(null)}
        />
      )}
    </div>
  );
}

function EstateCard({
  coin,
  onClick,
}: {
  coin: Coin;
  onClick: () => void;
}) {
  const price = coin.asking_price || coin.estimated_value;
  const listedDate = coin.listed_at
    ? new Date(coin.listed_at).toLocaleDateString()
    : null;

  return (
    <div
      onClick={onClick}
      className="card cursor-pointer hover:shadow-xl transition-shadow group border-gold-200"
    >
      <div className="relative h-44 bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
        {coin.images?.obverse ? (
          <img
            src={coin.images.obverse}
            alt={coin.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform"
          />
        ) : (
          <span className="text-5xl opacity-30">🪙</span>
        )}
        <span className="absolute top-2 left-2 bg-gold-400 text-navy-500 text-xs font-bold px-2 py-1 rounded">
          🏠 Estate
        </span>
        {listedDate && (
          <span className="absolute bottom-2 right-2 bg-black/60 text-white text-xs px-2 py-0.5 rounded">
            Listed {listedDate}
          </span>
        )}
      </div>

      <h3 className="font-bold text-navy-500 text-sm mb-1 line-clamp-1">
        {coin.title}
      </h3>

      <div className="flex items-center gap-2 mb-2">
        {coin.ai_grade && (
          <span className="bg-navy-500 text-gold-400 text-xs font-bold px-2 py-0.5 rounded">
            {coin.ai_grade}
          </span>
        )}
        {coin.year && (
          <span className="text-xs text-navy-300">
            {coin.year}
            {coin.mint_mark ? `-${coin.mint_mark}` : ''}
          </span>
        )}
      </div>

      <div className="flex items-center justify-between">
        <p className="text-lg font-bold text-green-600">
          {price ? `$${price.toLocaleString()}` : 'Price TBD'}
        </p>
        <span className="text-xs text-navy-300">
          {coin.coin_type || 'Unclassified'}
        </span>
      </div>
    </div>
  );
}

function EstateCoinModal({
  coin,
  onClose,
}: {
  coin: Coin;
  onClose: () => void;
}) {
  const price = coin.asking_price || coin.estimated_value;

  return (
    <div
      className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4"
      onClick={onClose}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl max-w-lg w-full max-h-[80vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="relative h-56 bg-gray-100 rounded-t-2xl flex items-center justify-center overflow-hidden">
          {coin.images?.obverse ? (
            <img
              src={coin.images.obverse}
              alt={coin.title}
              className="w-full h-full object-cover"
            />
          ) : (
            <span className="text-7xl opacity-20">🪙</span>
          )}
          <button
            onClick={onClose}
            className="absolute top-3 right-3 bg-white/80 backdrop-blur rounded-full w-8 h-8 flex items-center justify-center text-navy-500 hover:bg-white"
          >
            ✕
          </button>
          <span className="absolute top-3 left-3 bg-gold-400 text-navy-500 text-xs font-bold px-2 py-1 rounded">
            🏠 Estate Inventory
          </span>
        </div>

        <div className="p-6">
          <h2 className="text-xl font-bold text-navy-500 mb-3">{coin.title}</h2>

          <div className="bg-gold-50 border border-gold-200 rounded-lg p-3 mb-4 text-sm text-navy-500">
            🏠 This coin comes from an estate collection. Estate sellers are
            often motivated and may accept reasonable offers.
          </div>

          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-navy-300">Grade</p>
              <p className="text-lg font-bold text-navy-500">
                {coin.ai_grade || '—'}
              </p>
            </div>
            <div className="text-center p-3 bg-gray-50 rounded-lg">
              <p className="text-xs text-navy-300">Confidence</p>
              <p className="text-lg font-bold text-navy-500">
                {coin.ai_confidence
                  ? `${(coin.ai_confidence * 100).toFixed(0)}%`
                  : '—'}
              </p>
            </div>
            <div className="text-center p-3 bg-green-50 rounded-lg">
              <p className="text-xs text-navy-300">Price</p>
              <p className="text-lg font-bold text-green-600">
                {price ? `$${price.toLocaleString()}` : 'TBD'}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 text-sm mb-4">
            {coin.coin_type && (
              <div className="flex justify-between p-2 bg-gray-50 rounded">
                <span className="text-navy-300">Type</span>
                <span className="font-medium text-navy-500">
                  {coin.coin_type}
                </span>
              </div>
            )}
            {coin.year && (
              <div className="flex justify-between p-2 bg-gray-50 rounded">
                <span className="text-navy-300">Year</span>
                <span className="font-medium text-navy-500">{coin.year}</span>
              </div>
            )}
            {coin.mint_mark && (
              <div className="flex justify-between p-2 bg-gray-50 rounded">
                <span className="text-navy-300">Mint</span>
                <span className="font-medium text-navy-500">
                  {coin.mint_mark}
                </span>
              </div>
            )}
          </div>

          {coin.images && Object.keys(coin.images).length > 1 && (
            <div className="flex gap-2 mb-4">
              {Object.entries(coin.images).map(([label, url]) => (
                <div
                  key={label}
                  className="w-16 h-16 bg-gray-100 rounded-lg overflow-hidden"
                >
                  <img
                    src={url}
                    alt={label}
                    className="w-full h-full object-cover"
                  />
                </div>
              ))}
            </div>
          )}

          <button className="btn-primary w-full" onClick={onClose}>
            Contact Seller
          </button>
        </div>
      </div>
    </div>
  );
}
