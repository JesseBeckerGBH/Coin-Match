/**
 * API client for CoinMatch backend.
 */

import axios from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('coinmatch_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

// ──────── Auth ────────

export const signup = (data: {
  email: string;
  password: string;
  name: string;
  user_type?: string;
}) => api.post('/api/auth/signup', data);

export const login = (data: { email: string; password: string }) =>
  api.post('/api/auth/login', data);

export const getMe = () => api.get('/api/auth/me');

// ──────── Coins ────────

export const createCoin = (data: any) => api.post('/api/coins', data);

export const listCoins = (params?: Record<string, any>) =>
  api.get('/api/coins', { params });

export const getCoin = (id: string) => api.get(`/api/coins/${id}`);

export const freshInventory = (params?: { page?: number; per_page?: number }) =>
  api.get('/api/coins/fresh-inventory', { params });

export const uploadCoinImages = (coinId: string, formData: FormData) =>
  api.post(`/api/coins/${coinId}/upload-images`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });

export const gradeCoin = (coinId: string) =>
  api.post(`/api/coins/${coinId}/grade`);

export const listCoin = (coinId: string) =>
  api.post(`/api/coins/${coinId}/list`);

// ──────── Want List ────────

export const createWant = (data: any) => api.post('/api/want-list', data);
export const listWants = () => api.get('/api/want-list');
export const updateWant = (id: string, data: any) =>
  api.put(`/api/want-list/${id}`, data);
export const deleteWant = (id: string) => api.delete(`/api/want-list/${id}`);

// ──────── Transactions ────────

export const estimateCommission = (amount: number) =>
  api.get('/api/transactions/estimate-commission', { params: { amount } });

export const purchaseCoin = (coinId: string, offeredPrice?: number) =>
  api.post('/api/transactions/purchase', {
    coin_id: coinId,
    offered_price: offeredPrice,
  });

export const myPurchases = () => api.get('/api/transactions/my-purchases');
export const mySales = () => api.get('/api/transactions/my-sales');

// ──────── Billing ────────

export const startSellerOnboarding = () =>
  api.post('/api/billing/connect/onboard');

export const getConnectStatus = () => api.get('/api/billing/connect/status');

export const subscribe = (tier: 'pro' | 'dealer') =>
  api.post(`/api/billing/subscribe/${tier}`);

// ──────── Users ────────

export const updateProfile = (data: any) => api.put('/api/users/profile', data);
export const getDashboardStats = () => api.get('/api/users/dashboard-stats');

export default api;
