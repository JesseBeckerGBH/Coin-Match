'use client';

import { useState, useEffect } from 'react';
import { listCoins, estimateCommission } from '@/lib/api';
import Link from 'next/link';

const COIN_TYPES = [
  'Morgan Dollar', 'Peace Dollar', 'Lincoln Cent', 'Buffalo Nickel',
  'Mercury Dime', 'Walking Liberty Half Dollar', 'Kennedy Half Dollar',
  'Washington Quarter', 'Indian Head Cent', 'Saint-Gaudens',
];

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

export default function BrowsePage() {
  const [coins, setCoins] = useState<Coin[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [selectedCoin, setSelectedCoin] = useState<Coin | null>(null);

  // Filters
  const [filters, setFilters] = useState({
    coin_type: '',
    year_min: '',
    year_max: '',
    mint_mark: '',
    min_grade: '',
    price_min: '',
    price_max: '',
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  const loadCoins = async (p: number = 1) => {
    setLoading(true);
    try {
      const params: any = { page: p, per_page: 12 };
      if (filters.coin_type) params.coin_type = filters.coin_type;
      if (filters.year_min) params.year_min = parseInt(filters.year_min);
      if (filters.year_max) params.year_max = parseInt(filters.year_max);
      if (filters.mint_mark) params.mint_mark = filters.mint_mark;
      if (filters.min_grade) params.min_grade = parseInt(filters.min_grade);
      if (filters.price_min) params.price_min = parseFloat(filters.price_min);
      if (filters.price_max) params.price_max = parseFloat(filters.price_max);
      params.sort_by = filters.sort_by;
      params.sort_order = filters.sort_order;

      const res = await listCoins(params);
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
    loadCoins();
  }, []);

  const handleSearch = () => {
    loadCoins(1);
  };

  const handleClear = () => {
    setFilters({
      coin_type: '',
      year_min: '',
      year_max: '',
      mint_mark: '',
      min_grade: '',
      price_min: '',
      price_max: '',
      sort_by: 'created_at',
      sort_order: 'desc',
    });
    loadCoins(1);
  };

  const totalPages = Math.ceil(total / 12);

  return (
    <div className="max-w-7xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold text-navy-500 mb-2">
        🔍 Browse Marketplace
      </h1>
      <p className="text-navy-300 mb-6">
        {total} coin{total !== 1 ? 's' : ''} available
      </p>

      {/* Filters */}
      <div className="card mb-6">
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-3">
          <select
            value={filters.coin_type}
            onChange={(e) =>
              setFilters({ ...filters, coin_type: e.target.value })
            }
            className="px-3 py-2 border-2 border-gray-200 rounded-lg text-sm bg-white focus:border-gold-400 focus:outline-none"
          >
            <option value="">All Types</option>
            {COIN_TYPES.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>

          <input
            type="number"
            value={filters.year_min}
            onChange={(e) =>
              setFilters({ ...filters, year_min: e.target.value })
            }
            placeholder="Year from"
            className="px-3 py-2 border-2 border-gray-200 rounded-lg text-sm focus:border-gold-400 focus:outline-none"
          />

          <input
            type="number"
            value={filters.year_max}
            onChange={(e) =>
              setFilters({ ...filters, year_max: e.target.value })
            }
            placeholder="Year to"
            className="px-3 py-2 border-2 border-gray-200 rounded-lg text-sm focus:border-gold-400 focus:outline-none"
          />

          <select
            value={filters.mint_mark}
            onChange={(e) =>
              setFilters({ ...filters, mint_mark: e.target.value })
            }
            className="px-3 py-2 border-2 border-gray-200 rounded-lg text-sm bg-white focus:border-gold-400 focus:outline-none"
          >
            <option value="">Any Mint</option>
            {['P', 'D', 'S', 'O', 'CC', 'W'].map((m) => (
              <option key={m} value={m}>
                {m}
              </option>
            ))}
          </select>

          <input
            type="number"
            value={filters.price_max}
            onChange={(e) =>
              setFilters({ ...filters, price_max: e.target.value })
            }
            placeholder="Max price"
            className="px-3 py-2 border-2 border-gray-200 rounded-lg text-sm focus:border-gold-400 focus:outline-none"
          />

          <select
            value={`${filters.sort_by}:${filters.sort_order}`}
            onChange={(e) => {
              const [sort_by, sort_order] = e.target.value.split(':');
              setFilters({ ...filters, sort_by, sort_order });
            }}
            className="px-3 py-2 border-2 border-gray-200 rounded-lg text-sm bg-white focus:border-gold-400 focus:outline-none"
          >
            <option value="created_at:desc">Newest First</option>
            <option value="created_at:asc">Oldest First</option>
            <option value="asking_price:asc">Price: Low → High</option>
            <option value="asking_price:desc">Price: High → Low</option>
            <option value="ai_grade_numeric:desc">Grade: High → Low</option>
          </select>

          <div className="flex gap-2">
            <button
              onClick={handleSearch}
              className="btn-primary text-sm flex-1"
            >
              Search
            </button>
            <button
              onClick={handleClear}
              className="text-sm px-3 py-2 border-2 border-gray-200 rounded-lg hover:bg-gray-50 text-navy-400"
            >
              Clear
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {loading ? (
        <div className="text-center py-16">
          <span className="text-4xl animate-pulse">🪙</span>
          <p className="text-navy-300 mt-4">Searching marketplace...</p>
        </div>
      ) : coins.length === 0 ? (
        <div className="card text-center py-16">
          <span className="text-5xl mb-4 block">🔍</span>
          <h3 className="text-xl font-bold text-navy-500 mb-2">
            No coins found
          </h3>
          <p className="text-navy-300 mb-6">
            Try adjusting your filters or check back later — new coins are listed daily.
          </p>
          <Link href="/dashboard/wants" className="btn-primary inline-block">
            Set up a Want List Alert →
          </Link>
        </div>
      ) : (
        <>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {coins.map((coin) => (
              <CoinCard
                key={coin.id}
                coin={coin}
                onClick={() => setSelectedCoin(coin)}
              />
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-8">
              <button
                onClick={() => loadCoins(page - 1)}
                disabled={page <= 1}
                className="px-4 py-2 rounded-lg border border-gray-200 text-sm disabled:opacity-30 hover:bg-gray-50"
              >
                ← Prev
              </button>
              <span className="text-sm text-navy-300 px-4">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => loadCoins(page + 1)}
                disabled={page >= totalPages}
                className="px-4 py-2 rounded-lg border border-gray-200 text-sm disabled:opacity-30 hover:bg-gray-50"
              >
                Next →
              </button>
            </div>
          )}
        </>
      )}

      {/* Coin detail modal */}
      {selectedCoin && (
        <CoinModal
          coin={selectedCoin}
          onClose={() => setSelectedCoin(null)}
        />
      )}
    </div>
  );
}

function CoinCard({
  coin,
  onClick,
}: {
  coin: Coin;
  onClick: () => void;
}) {
  const price = coin.asking_price || coin.estimated_value;

  return (
    <div
      onClick={onClick}
      className="card cursor-pointer hover:shadow-xl transition-shadow group"
    >
      {/* Image */}
      <div className="relative h-40 bg-gray-100 rounded-lg mb-3 flex items-center justify-center overflow-hidden">
        {coin.images?.obverse ? (
          <img
            src={coin.images.obverse}
            alt={coin.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform"
          />
        ) : (
          <span className="text-5xl opacity-30">🪙</span>
        )}
        {coin.is_estate && (
          <span className="absolute top-2 left-2 bg-gold-400 text-navy-500 text-xs font-bold px-2 py-0.5 rounded">
            Estate
          </span>
        )}
      </div>

      {/* Info */}
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
        {coin.ai_confidence && (
          <span className="text-xs text-navy-300">
            {(coin.ai_confidence * 100).toFixed(0)}% conf.
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

function CoinModal({
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
        {/* Image */}
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
          {coin.is_estate && (
            <span className="absolute top-3 left-3 bg-gold-400 text-navy-500 text-xs font-bold px-2 py-1 rounded">
              🏠 Estate Inventory
            </span>
          )}
        </div>

        <div className="p-6">
          <h2 className="text-xl font-bold text-navy-500 mb-2">{coin.title}</h2>

          {/* Grade and price */}
          <div className="grid grid-cols-3 gap-3 mb-4">
            <div className="text-center p-3 bg-gold-50 rounded-lg">
              <p className="text-xs text-navy-300">Grade</p>
              <p className="text-lg font-bold text-navy-500">
                {coin.ai_grade || '—'}
              </p>
            </div>
            <div className="text-center p-3 bg-gold-50 rounded-lg">
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

          {/* Details */}
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
            <div className="flex justify-between p-2 bg-gray-50 rounded">
              <span className="text-navy-300">Status</span>
              <span className="font-medium text-navy-500">{coin.status}</span>
            </div>
          </div>

          {/* Image thumbnails */}
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
