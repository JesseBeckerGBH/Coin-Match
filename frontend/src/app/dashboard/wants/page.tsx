'use client';

import { useState, useEffect } from 'react';
import { createWant, listWants, updateWant, deleteWant, getMe } from '@/lib/api';

const COIN_TYPES = [
  'Morgan Dollar', 'Peace Dollar', 'Lincoln Cent', 'Buffalo Nickel',
  'Mercury Dime', 'Walking Liberty Half Dollar', 'Kennedy Half Dollar',
  'Washington Quarter', 'Standing Liberty Quarter', 'Franklin Half Dollar',
  'Indian Head Cent', 'Saint-Gaudens', 'Trade Dollar', 'Barber',
];

const GRADE_LABELS: Record<number, string> = {
  1: 'P-1', 4: 'G-4', 8: 'VG-8', 12: 'F-12', 20: 'VF-20',
  30: 'VF-30', 40: 'EF-40', 50: 'AU-50', 58: 'AU-58',
  60: 'MS-60', 63: 'MS-63', 65: 'MS-65', 67: 'MS-67', 70: 'MS-70',
};

interface WantItem {
  id: string;
  coin_type: string | null;
  series: string | null;
  year_min: number | null;
  year_max: number | null;
  mint_marks: string[] | null;
  min_grade_numeric: number | null;
  max_grade_numeric: number | null;
  price_min: number | null;
  price_max: number | null;
  notes: string | null;
  notify_immediately: boolean;
  is_active: boolean;
  created_at: string;
}

export default function WantsPage() {
  const [wants, setWants] = useState<WantItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [userTier, setUserTier] = useState('free');
  const [form, setForm] = useState({
    coin_type: '',
    year_min: '',
    year_max: '',
    mint_marks: [] as string[],
    min_grade_numeric: '',
    max_grade_numeric: '',
    price_min: '',
    price_max: '',
    notes: '',
    notify_immediately: true,
  });

  const loadWants = async () => {
    try {
      const res = await listWants();
      setWants(res.data);
    } catch {
      setError('Failed to load want list');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadWants();
    getMe().then((res) => setUserTier(res.data.tier)).catch(() => {});
  }, []);

  const handleCreate = async () => {
    setError('');
    if (!form.coin_type) {
      setError('Coin type is required');
      return;
    }
    setSaving(true);
    try {
      const payload: any = {
        coin_type: form.coin_type,
        year_min: form.year_min ? parseInt(form.year_min) : undefined,
        year_max: form.year_max ? parseInt(form.year_max) : undefined,
        mint_marks: form.mint_marks.length > 0 ? form.mint_marks : undefined,
        min_grade_numeric: form.min_grade_numeric
          ? parseInt(form.min_grade_numeric)
          : undefined,
        max_grade_numeric: form.max_grade_numeric
          ? parseInt(form.max_grade_numeric)
          : undefined,
        price_min: form.price_min ? parseFloat(form.price_min) : undefined,
        price_max: form.price_max ? parseFloat(form.price_max) : undefined,
        notes: form.notes || undefined,
        notify_immediately: form.notify_immediately,
      };
      await createWant(payload);
      setForm({
        coin_type: '',
        year_min: '',
        year_max: '',
        mint_marks: [],
        min_grade_numeric: '',
        max_grade_numeric: '',
        price_min: '',
        price_max: '',
        notes: '',
        notify_immediately: true,
      });
      setShowForm(false);
      await loadWants();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create want');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (item: WantItem) => {
    try {
      await updateWant(item.id, { is_active: !item.is_active });
      await loadWants();
    } catch {
      setError('Failed to update');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Remove this from your want list?')) return;
    try {
      await deleteWant(id);
      await loadWants();
    } catch {
      setError('Failed to delete');
    }
  };

  const toggleMintMark = (mark: string) => {
    setForm((prev) => ({
      ...prev,
      mint_marks: prev.mint_marks.includes(mark)
        ? prev.mint_marks.filter((m) => m !== mark)
        : [...prev.mint_marks, mark],
    }));
  };

  const wantLimit = userTier === 'free' ? 5 : Infinity;
  const atLimit = wants.length >= wantLimit;

  return (
    <div className="max-w-4xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-navy-500">📋 Want List</h1>
          <p className="text-navy-300 mt-1">
            Tell us what coins you&apos;re looking for — we&apos;ll alert you when a
            match appears.
          </p>
        </div>
        {!showForm && (
          <button
            onClick={() => setShowForm(true)}
            disabled={atLimit}
            className="btn-primary disabled:opacity-50"
            title={atLimit ? 'Upgrade to Pro for unlimited wants' : ''}
          >
            + Add Want
          </button>
        )}
      </div>

      {atLimit && userTier === 'free' && (
        <div className="bg-gold-50 border border-gold-200 rounded-lg px-4 py-3 mb-6 flex items-center justify-between">
          <p className="text-sm text-navy-500">
            ⭐ Free accounts can have up to 5 want list items.
            Upgrade to Pro for unlimited.
          </p>
          <a
            href="/dashboard"
            className="text-gold-600 font-bold text-sm hover:text-gold-700"
          >
            Upgrade →
          </a>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Add want form */}
      {showForm && (
        <div className="card mb-6 space-y-4">
          <h2 className="text-lg font-bold text-navy-500">
            New Want List Item
          </h2>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Coin Type *
              </label>
              <select
                value={form.coin_type}
                onChange={(e) =>
                  setForm({ ...form, coin_type: e.target.value })
                }
                className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none bg-white text-sm"
              >
                <option value="">Select type...</option>
                {COIN_TYPES.map((t) => (
                  <option key={t} value={t}>
                    {t}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Mint Marks
              </label>
              <div className="flex flex-wrap gap-1">
                {['P', 'D', 'S', 'O', 'CC', 'W'].map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => toggleMintMark(m)}
                    className={`px-2.5 py-1 rounded text-xs font-bold border transition-colors ${
                      form.mint_marks.includes(m)
                        ? 'bg-gold-400 text-navy-500 border-gold-500'
                        : 'bg-white text-navy-300 border-gray-200 hover:border-gold-300'
                    }`}
                  >
                    {m}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Year Range
              </label>
              <div className="flex gap-2 items-center">
                <input
                  type="number"
                  value={form.year_min}
                  onChange={(e) =>
                    setForm({ ...form, year_min: e.target.value })
                  }
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none text-sm"
                  placeholder="From"
                />
                <span className="text-navy-300">—</span>
                <input
                  type="number"
                  value={form.year_max}
                  onChange={(e) =>
                    setForm({ ...form, year_max: e.target.value })
                  }
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none text-sm"
                  placeholder="To"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Grade Range (Sheldon)
              </label>
              <div className="flex gap-2 items-center">
                <select
                  value={form.min_grade_numeric}
                  onChange={(e) =>
                    setForm({ ...form, min_grade_numeric: e.target.value })
                  }
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none bg-white text-sm"
                >
                  <option value="">Min</option>
                  {Object.entries(GRADE_LABELS).map(([num, label]) => (
                    <option key={num} value={num}>
                      {label}
                    </option>
                  ))}
                </select>
                <span className="text-navy-300">—</span>
                <select
                  value={form.max_grade_numeric}
                  onChange={(e) =>
                    setForm({ ...form, max_grade_numeric: e.target.value })
                  }
                  className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none bg-white text-sm"
                >
                  <option value="">Max</option>
                  {Object.entries(GRADE_LABELS).map(([num, label]) => (
                    <option key={num} value={num}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Price Range
              </label>
              <div className="flex gap-2 items-center">
                <div className="relative flex-1">
                  <span className="absolute left-2.5 top-2.5 text-xs text-navy-300">
                    $
                  </span>
                  <input
                    type="number"
                    value={form.price_min}
                    onChange={(e) =>
                      setForm({ ...form, price_min: e.target.value })
                    }
                    className="w-full pl-6 pr-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none text-sm"
                    placeholder="Min"
                  />
                </div>
                <span className="text-navy-300">—</span>
                <div className="relative flex-1">
                  <span className="absolute left-2.5 top-2.5 text-xs text-navy-300">
                    $
                  </span>
                  <input
                    type="number"
                    value={form.price_max}
                    onChange={(e) =>
                      setForm({ ...form, price_max: e.target.value })
                    }
                    className="w-full pl-6 pr-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none text-sm"
                    placeholder="Max"
                  />
                </div>
              </div>
            </div>
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Notes
              </label>
              <input
                type="text"
                value={form.notes}
                onChange={(e) => setForm({ ...form, notes: e.target.value })}
                className="w-full px-3 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none text-sm"
                placeholder="e.g. Prefer rainbow toning, no cleaning"
              />
            </div>
          </div>

          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={form.notify_immediately}
              onChange={(e) =>
                setForm({ ...form, notify_immediately: e.target.checked })
              }
              className="w-4 h-4 accent-gold-400"
            />
            <span className="text-sm text-navy-400">
              Notify me immediately when a match is found
            </span>
          </label>

          <div className="flex gap-3">
            <button
              onClick={() => setShowForm(false)}
              className="btn-secondary flex-1"
            >
              Cancel
            </button>
            <button
              onClick={handleCreate}
              disabled={saving}
              className="btn-primary flex-1 disabled:opacity-50"
            >
              {saving ? 'Saving...' : 'Add to Want List'}
            </button>
          </div>
        </div>
      )}

      {/* Want list items */}
      {loading ? (
        <div className="text-center py-12">
          <span className="text-4xl animate-pulse">🔍</span>
        </div>
      ) : wants.length === 0 ? (
        <div className="card text-center py-12">
          <span className="text-5xl mb-4 block">📋</span>
          <h3 className="text-xl font-bold text-navy-500 mb-2">
            Your want list is empty
          </h3>
          <p className="text-navy-300 mb-6">
            Add coins you&apos;re looking for and we&apos;ll match them with new
            listings automatically.
          </p>
          {!showForm && (
            <button onClick={() => setShowForm(true)} className="btn-primary">
              + Add Your First Want
            </button>
          )}
        </div>
      ) : (
        <div className="space-y-3">
          {wants.map((item) => (
            <div
              key={item.id}
              className={`card flex items-center gap-4 ${
                !item.is_active ? 'opacity-50' : ''
              }`}
            >
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <h3 className="font-bold text-navy-500">
                    {item.coin_type || 'Any Type'}
                  </h3>
                  {item.is_active && (
                    <span className="bg-green-100 text-green-700 text-xs font-bold px-2 py-0.5 rounded">
                      Active
                    </span>
                  )}
                  {!item.is_active && (
                    <span className="bg-gray-100 text-gray-500 text-xs font-bold px-2 py-0.5 rounded">
                      Paused
                    </span>
                  )}
                </div>
                <div className="flex flex-wrap gap-3 text-sm text-navy-300">
                  {(item.year_min || item.year_max) && (
                    <span>
                      📅 {item.year_min || '?'}–{item.year_max || '?'}
                    </span>
                  )}
                  {item.mint_marks && item.mint_marks.length > 0 && (
                    <span>🏛️ {item.mint_marks.join(', ')}</span>
                  )}
                  {item.min_grade_numeric && (
                    <span>
                      ⭐ {GRADE_LABELS[item.min_grade_numeric] || item.min_grade_numeric}
                      {item.max_grade_numeric
                        ? `–${GRADE_LABELS[item.max_grade_numeric] || item.max_grade_numeric}`
                        : '+'}
                    </span>
                  )}
                  {(item.price_min || item.price_max) && (
                    <span>
                      💰 ${item.price_min?.toLocaleString() || '0'}–$
                      {item.price_max?.toLocaleString() || '∞'}
                    </span>
                  )}
                </div>
                {item.notes && (
                  <p className="text-xs text-navy-300 mt-1 italic">
                    {item.notes}
                  </p>
                )}
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => handleToggle(item)}
                  className="text-sm px-3 py-1.5 rounded-lg border border-gray-200 hover:bg-gray-50 text-navy-400"
                  title={item.is_active ? 'Pause' : 'Resume'}
                >
                  {item.is_active ? '⏸' : '▶️'}
                </button>
                <button
                  onClick={() => handleDelete(item.id)}
                  className="text-sm px-3 py-1.5 rounded-lg border border-red-200 hover:bg-red-50 text-red-500"
                  title="Delete"
                >
                  🗑
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
