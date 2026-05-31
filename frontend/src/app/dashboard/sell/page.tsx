'use client';

import { useState, useEffect, useRef } from 'react';
import { createCoin, uploadCoinImages, gradeCoin, listCoin, getMe } from '@/lib/api';

const COIN_TYPES = [
  'Morgan Dollar', 'Peace Dollar', 'Lincoln Cent', 'Buffalo Nickel',
  'Mercury Dime', 'Walking Liberty Half Dollar', 'Kennedy Half Dollar',
  'Washington Quarter', 'Standing Liberty Quarter', 'Franklin Half Dollar',
  'Indian Head Cent', 'Saint-Gaudens', 'Trade Dollar', 'Barber',
  'Other',
];

const MINT_MARKS = ['P', 'D', 'S', 'O', 'CC', 'W', 'C', 'None'];

type Step = 'details' | 'photos' | 'grade' | 'price' | 'listed';

interface CoinDraft {
  id?: string;
  title: string;
  description: string;
  coin_type: string;
  year: string;
  mint_mark: string;
  denomination: string;
  series: string;
  country: string;
  metal_type: string;
  asking_price: string;
  provenance_notes: string;
}

interface GradeData {
  grade: string;
  grade_numeric: number;
  confidence: number;
  luster_score: number;
  strike_score: number;
  estimated_value: number | null;
  notes: string;
}

export default function SellPage() {
  const [step, setStep] = useState<Step>('details');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [userType, setUserType] = useState('');
  const [coin, setCoin] = useState<CoinDraft>({
    title: '',
    description: '',
    coin_type: '',
    year: '',
    mint_mark: '',
    denomination: '',
    series: '',
    country: 'United States',
    metal_type: '',
    asking_price: '',
    provenance_notes: '',
  });
  const [images, setImages] = useState<{ [key: string]: File | null }>({
    obverse: null,
    reverse: null,
    edge: null,
    detail: null,
  });
  const [previews, setPreviews] = useState<{ [key: string]: string }>({});
  const [gradeResult, setGradeResult] = useState<GradeData | null>(null);
  const [listResult, setListResult] = useState<any>(null);

  useEffect(() => {
    getMe().then((res) => setUserType(res.data.user_type)).catch(() => {});
  }, []);

  const handleImageSelect = (label: string, file: File | null) => {
    setImages((prev) => ({ ...prev, [label]: file }));
    if (file) {
      const url = URL.createObjectURL(file);
      setPreviews((prev) => ({ ...prev, [label]: url }));
    } else {
      setPreviews((prev) => {
        const copy = { ...prev };
        delete copy[label];
        return copy;
      });
    }
  };

  const handleCreateCoin = async () => {
    setError('');
    if (!coin.title.trim()) {
      setError('Title is required');
      return;
    }
    setLoading(true);
    try {
      const payload: any = {
        title: coin.title.trim(),
        description: coin.description || undefined,
        coin_type: coin.coin_type || undefined,
        year: coin.year ? parseInt(coin.year) : undefined,
        mint_mark: coin.mint_mark || undefined,
        denomination: coin.denomination || undefined,
        series: coin.series || undefined,
        country: coin.country,
        metal_type: coin.metal_type || undefined,
        asking_price: coin.asking_price ? parseFloat(coin.asking_price) : undefined,
        provenance_notes: coin.provenance_notes || undefined,
      };
      const res = await createCoin(payload);
      setCoin((prev) => ({ ...prev, id: res.data.id }));
      setStep('photos');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to create coin listing');
    } finally {
      setLoading(false);
    }
  };

  const handleUploadAndGrade = async () => {
    setError('');
    if (!images.obverse || !images.reverse) {
      setError('Obverse and reverse photos are required');
      return;
    }
    if (!coin.id) return;
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('obverse', images.obverse);
      formData.append('reverse', images.reverse);
      if (images.edge) formData.append('edge', images.edge);
      if (images.detail) formData.append('detail', images.detail);

      await uploadCoinImages(coin.id, formData);
      const gradeRes = await gradeCoin(coin.id);
      setGradeResult(gradeRes.data);
      setStep('grade');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to upload/grade');
    } finally {
      setLoading(false);
    }
  };

  const handleList = async () => {
    setError('');
    if (!coin.id) return;
    setLoading(true);
    try {
      const res = await listCoin(coin.id);
      setListResult(res.data);
      setStep('listed');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to list coin');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-6 py-8">
      <h1 className="text-3xl font-bold text-navy-500 mb-2">📸 Sell a Coin</h1>
      <p className="text-navy-300 mb-8">
        {userType === 'estate_seller'
          ? 'Upload photos of inherited coins for a free AI assessment and instant buyer matching.'
          : 'List your coin on the marketplace with AI grading and automatic buyer matching.'}
      </p>

      {/* Progress steps */}
      <div className="flex items-center gap-2 mb-8">
        {(['details', 'photos', 'grade', 'listed'] as Step[]).map((s, i) => (
          <div key={s} className="flex items-center gap-2">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                step === s
                  ? 'bg-gold-400 text-navy-500'
                  : ['details', 'photos', 'grade', 'listed'].indexOf(step) > i
                    ? 'bg-green-500 text-white'
                    : 'bg-gray-200 text-gray-400'
              }`}
            >
              {['details', 'photos', 'grade', 'listed'].indexOf(step) > i ? '✓' : i + 1}
            </div>
            {i < 3 && (
              <div
                className={`w-12 h-0.5 ${
                  ['details', 'photos', 'grade', 'listed'].indexOf(step) > i
                    ? 'bg-green-500'
                    : 'bg-gray-200'
                }`}
              />
            )}
          </div>
        ))}
        <div className="ml-2 text-sm text-navy-300">
          {step === 'details' && 'Coin Details'}
          {step === 'photos' && 'Upload Photos'}
          {step === 'grade' && 'AI Grade'}
          {step === 'listed' && 'Listed!'}
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      {/* Step 1: Details */}
      {step === 'details' && (
        <div className="card space-y-4">
          <h2 className="text-xl font-bold text-navy-500">Coin Details</h2>

          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">
              Title *
            </label>
            <input
              type="text"
              value={coin.title}
              onChange={(e) => setCoin({ ...coin, title: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
              placeholder="e.g. 1921 Morgan Silver Dollar — Philadelphia"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Coin Type
              </label>
              <select
                value={coin.coin_type}
                onChange={(e) => setCoin({ ...coin, coin_type: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none bg-white"
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
                Year
              </label>
              <input
                type="number"
                value={coin.year}
                onChange={(e) => setCoin({ ...coin, year: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
                placeholder="1921"
                min={1700}
                max={2026}
              />
            </div>
          </div>

          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Mint Mark
              </label>
              <select
                value={coin.mint_mark}
                onChange={(e) => setCoin({ ...coin, mint_mark: e.target.value })}
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none bg-white"
              >
                <option value="">Select...</option>
                {MINT_MARKS.map((m) => (
                  <option key={m} value={m === 'None' ? '' : m}>
                    {m}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Denomination
              </label>
              <input
                type="text"
                value={coin.denomination}
                onChange={(e) =>
                  setCoin({ ...coin, denomination: e.target.value })
                }
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
                placeholder="$1.00"
              />
            </div>
            <div>
              <label className="block text-sm font-bold text-navy-500 mb-1">
                Metal
              </label>
              <input
                type="text"
                value={coin.metal_type}
                onChange={(e) =>
                  setCoin({ ...coin, metal_type: e.target.value })
                }
                className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
                placeholder="Silver"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">
              Description
            </label>
            <textarea
              value={coin.description}
              onChange={(e) => setCoin({ ...coin, description: e.target.value })}
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
              rows={3}
              placeholder="Any notable details, toning, errors, varieties..."
            />
          </div>

          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">
              Asking Price (optional — AI will estimate if blank)
            </label>
            <div className="relative">
              <span className="absolute left-3 top-2.5 text-navy-300">$</span>
              <input
                type="number"
                value={coin.asking_price}
                onChange={(e) =>
                  setCoin({ ...coin, asking_price: e.target.value })
                }
                className="w-full pl-8 pr-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
                placeholder="0.00"
                min={0}
                step={0.01}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-bold text-navy-500 mb-1">
              Provenance / History
            </label>
            <textarea
              value={coin.provenance_notes}
              onChange={(e) =>
                setCoin({ ...coin, provenance_notes: e.target.value })
              }
              className="w-full px-4 py-2 border-2 border-gray-200 rounded-lg focus:border-gold-400 focus:outline-none"
              rows={2}
              placeholder="Where did this coin come from? Estate, family collection, purchased..."
            />
          </div>

          <button
            onClick={handleCreateCoin}
            disabled={loading}
            className="btn-primary w-full disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Continue to Photos →'}
          </button>
        </div>
      )}

      {/* Step 2: Photos */}
      {step === 'photos' && (
        <div className="card space-y-6">
          <h2 className="text-xl font-bold text-navy-500">Upload Photos</h2>
          <p className="text-navy-300 text-sm">
            Minimum: obverse (front) + reverse (back). Add edge and detail shots
            for higher grading confidence.
          </p>

          <div className="grid grid-cols-2 gap-4">
            {(['obverse', 'reverse', 'edge', 'detail'] as const).map(
              (label) => (
                <ImageUpload
                  key={label}
                  label={label}
                  required={label === 'obverse' || label === 'reverse'}
                  preview={previews[label]}
                  onSelect={(file) => handleImageSelect(label, file)}
                />
              )
            )}
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep('details')}
              className="btn-secondary flex-1"
            >
              ← Back
            </button>
            <button
              onClick={handleUploadAndGrade}
              disabled={loading}
              className="btn-primary flex-1 disabled:opacity-50"
            >
              {loading ? '🤖 Grading...' : '🤖 Upload & Grade'}
            </button>
          </div>
        </div>
      )}

      {/* Step 3: Grade Result */}
      {step === 'grade' && gradeResult && (
        <div className="space-y-6">
          <div className="card">
            <h2 className="text-xl font-bold text-navy-500 mb-4">
              AI Grading Result
            </h2>

            <div className="grid grid-cols-3 gap-4 mb-6">
              <div className="text-center p-4 bg-gold-50 rounded-xl">
                <p className="text-sm text-navy-300 mb-1">Grade</p>
                <p className="text-3xl font-bold text-navy-500">
                  {gradeResult.grade}
                </p>
              </div>
              <div className="text-center p-4 bg-gold-50 rounded-xl">
                <p className="text-sm text-navy-300 mb-1">Confidence</p>
                <p className="text-3xl font-bold text-navy-500">
                  {(gradeResult.confidence * 100).toFixed(0)}%
                </p>
              </div>
              <div className="text-center p-4 bg-gold-50 rounded-xl">
                <p className="text-sm text-navy-300 mb-1">Est. Value</p>
                <p className="text-3xl font-bold text-green-600">
                  {gradeResult.estimated_value
                    ? `$${gradeResult.estimated_value.toLocaleString()}`
                    : 'N/A'}
                </p>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <span className="text-xl">✨</span>
                <div>
                  <p className="text-xs text-navy-300">Luster Score</p>
                  <p className="font-bold text-navy-500">
                    {gradeResult.luster_score}/10
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <span className="text-xl">🔨</span>
                <div>
                  <p className="text-xs text-navy-300">Strike Score</p>
                  <p className="font-bold text-navy-500">
                    {gradeResult.strike_score}/10
                  </p>
                </div>
              </div>
            </div>

            {gradeResult.notes && (
              <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 text-sm text-blue-800">
                💡 {gradeResult.notes}
              </div>
            )}
          </div>

          <div className="card">
            <h3 className="font-bold text-navy-500 mb-3">
              Ready to list this coin?
            </h3>
            <p className="text-navy-300 text-sm mb-4">
              Publishing will make your coin visible to all CoinMatch buyers and
              automatically match it with collectors whose want lists match your
              coin&apos;s attributes.
            </p>
            <div className="flex gap-3">
              <button
                onClick={() => setStep('photos')}
                className="btn-secondary flex-1"
              >
                ← Re-upload
              </button>
              <button
                onClick={handleList}
                disabled={loading}
                className="btn-primary flex-1 disabled:opacity-50"
              >
                {loading ? 'Publishing...' : '🚀 List on Marketplace'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Step 4: Listed! */}
      {step === 'listed' && listResult && (
        <div className="card text-center py-12">
          <div className="text-6xl mb-4">🎉</div>
          <h2 className="text-2xl font-bold text-navy-500 mb-3">
            Coin Listed Successfully!
          </h2>
          <p className="text-navy-300 mb-2">
            Your coin is now live on the CoinMatch marketplace.
          </p>
          {listResult.matches_found > 0 && (
            <p className="text-green-600 font-bold mb-6">
              🎯 {listResult.matches_found} buyer
              {listResult.matches_found > 1 ? 's' : ''} already matched!
            </p>
          )}
          {listResult.matches_found === 0 && (
            <p className="text-navy-300 mb-6">
              No matches yet — buyers will be notified as their want lists
              update.
            </p>
          )}
          <div className="flex gap-3 justify-center">
            <button
              onClick={() => {
                setCoin({
                  title: '',
                  description: '',
                  coin_type: '',
                  year: '',
                  mint_mark: '',
                  denomination: '',
                  series: '',
                  country: 'United States',
                  metal_type: '',
                  asking_price: '',
                  provenance_notes: '',
                });
                setImages({ obverse: null, reverse: null, edge: null, detail: null });
                setPreviews({});
                setGradeResult(null);
                setListResult(null);
                setStep('details');
              }}
              className="btn-primary"
            >
              📸 List Another Coin
            </button>
            <a href="/dashboard/browse" className="btn-secondary inline-block">
              Browse Marketplace
            </a>
          </div>
        </div>
      )}
    </div>
  );
}

function ImageUpload({
  label,
  required,
  preview,
  onSelect,
}: {
  label: string;
  required: boolean;
  preview?: string;
  onSelect: (file: File | null) => void;
}) {
  const inputRef = useRef<HTMLInputElement>(null);
  const displayLabel = label.charAt(0).toUpperCase() + label.slice(1);

  return (
    <div
      onClick={() => inputRef.current?.click()}
      className={`relative border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-colors min-h-[140px] flex flex-col items-center justify-center ${
        preview
          ? 'border-green-400 bg-green-50'
          : required
            ? 'border-gold-400 hover:bg-gold-50'
            : 'border-gray-200 hover:bg-gray-50'
      }`}
    >
      <input
        ref={inputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={(e) => onSelect(e.target.files?.[0] || null)}
      />
      {preview ? (
        <>
          <img
            src={preview}
            alt={label}
            className="w-20 h-20 object-cover rounded-lg mb-2"
          />
          <p className="text-xs text-green-600 font-bold">
            ✓ {displayLabel}
          </p>
        </>
      ) : (
        <>
          <span className="text-3xl mb-2">📷</span>
          <p className="text-sm font-bold text-navy-500">{displayLabel}</p>
          <p className="text-xs text-navy-300">
            {required ? 'Required' : 'Optional'}
          </p>
        </>
      )}
    </div>
  );
}
