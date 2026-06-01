# 🪙 CoinMatch by JBAnalytics

**AI-Powered Numismatics Marketplace** — The smartest way to buy and sell coins.

CoinMatch connects coin collectors with estate sellers through instant AI grading and intelligent buyer-seller matching. The lowest fees in numismatics: **3% → 1%** tiered commission ($10 minimum) vs Heritage's 25-35%.

## 🎯 The Problem We Solve

- **Heritage Auctions** takes 25-35% in total fees
- **Local dealers** pay 40-60 cents on the dollar
- **eBay** has no curation, no grading, and fraud risk
- **Estate sellers** (people who inherited coins) get ripped off because they don't know what their coins are worth

CoinMatch fixes all of this with AI grading, direct matching, and transparent tiered pricing.

## ⚡ Key Features

### For Collectors (Buyers)
- **Want List Builder** — specify exactly what you're looking for (coin type, grade range, price range, mint marks)
- **Fresh Estate Inventory Alerts** — Pro/Dealer members get 24h early access to new estate listings
- **AI-Graded Listings** — every coin comes with a Sheldon scale grade (1-70), confidence score, and estimated value
- **Direct Matching** — no bidding wars, no auction delays

### For Estate Sellers
- **Zero subscription** — no monthly fee, ever
- **Free AI Grading** — upload 2-4 photos, get an instant grade and value estimate
- **Direct buyer matching** — connected with verified collectors who want exactly what you have
- **Transparent fees** — tiered commission only on successful sale

### Tiered Commission Schedule

Sellers pay the **greater of $10 or the tiered rate**. The $10 floor covers
fixed processing + AI grading costs on tiny sales; the tiered rate scales down
so high-value estate sales pay the headline 1% rate.

| Sale Value | Commission Rate | Example Fee |
|-----------|----------------|-------------|
| $0 – $500 | 3.0% (min $10) | $15 on a $500 coin |
| $501 – $2,000 | 2.5% | $50 on a $2,000 coin |
| $2,001 – $10,000 | 2.0% | $200 on a $10,000 coin |
| $10,001 – $50,000 | 1.5% | $750 on a $50,000 coin |
| $50,001+ | **1.0%** | **$1,000** on a $100k sale (vs Heritage's $15,000+) |

### Subscription Tiers
| Tier | Price | Benefits |
|------|-------|---------|
| Free Buyer | $0/mo | Browse, 5 want-list items, 3% buyer commission |
| Pro Collector | $19/mo | 24h early estate access, unlimited wants, 1.5% commission |
| Dealer | $99/mo | Instant alerts, API access, batch tools, 0.75% commission |
| Estate Seller | Always free | Commission only on successful sale |

## 🏗️ Tech Stack

- **Backend:** FastAPI (Python 3.11)
- **Frontend:** Next.js 14 + React 18 + Tailwind CSS
- **Database:** PostgreSQL
- **Cache:** Redis
- **Payments:** Stripe Connect (marketplace payouts)
- **Deployment:** Railway (two services: backend Docker + frontend Docker, plus Postgres + Redis plugins)
- **AI Grading:** Claude Opus 4.7 Vision (Anthropic API), heuristic fallback for local dev

## 📂 Project Structure

```
coinmatch/
├── backend/
│   ├── app/
│   │   ├── api/routes/     # Auth, coins, want-list, transactions, billing, users
│   │   ├── models/         # SQLAlchemy models (User, Coin, WantList, Transaction, Match)
│   │   ├── schemas/        # Pydantic request/response models
│   │   ├── services/       # Commission engine, matching, auth, Stripe Connect
│   │   └── main.py         # FastAPI application
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js pages (landing, auth, dashboard)
│   │   ├── components/     # Reusable React components
│   │   └── lib/            # API client, utilities
│   └── package.json
├── engine/
│   ├── grading/            # AI coin grading (V1 rule-based, V2 ML)
│   ├── matching/           # Buyer-seller matching utilities
│   └── scraping/           # Estate seller detection (Phase 2)
├── railway.toml
└── README.md
```

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

### Environment Variables
```env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/coinmatch

# Redis
REDIS_URL=redis://localhost:6379

# Auth
JWT_SECRET=<generate at https://generate-secret.vercel.app/64>

# Stripe Connect
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Claude Vision (AI grader)
ANTHROPIC_API_KEY=sk-ant-...

# Google OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...

# App
APP_ENV=production
APP_URL=https://getcoinmatch.com
CORS_ORIGINS=https://getcoinmatch.com
OWNER_EMAIL=jessebecker2021@gmail.com
PORT=8000
```

#### Frontend env (second Railway service)
```env
NEXT_PUBLIC_API_URL=https://<your-backend-service>.up.railway.app
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/signup` | Register (buyer/estate_seller/dealer) |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/me` | Current user |
| GET | `/api/auth/oauth/google` | Google OAuth |
| POST | `/api/coins` | Create listing |
| GET | `/api/coins` | Search/filter listings |
| GET | `/api/coins/fresh-inventory` | Estate coins (Pro/Dealer early access) |
| POST | `/api/coins/{id}/upload-images` | Upload coin photos |
| POST | `/api/coins/{id}/grade` | Trigger AI grading |
| POST | `/api/coins/{id}/list` | Publish + trigger matching |
| POST | `/api/want-list` | Add to want list |
| GET | `/api/want-list` | View want list |
| GET | `/api/transactions/estimate-commission` | Preview fees |
| POST | `/api/transactions/purchase` | Buy a coin |
| POST | `/api/billing/connect/onboard` | Seller Stripe setup |
| POST | `/api/billing/subscribe/{tier}` | Subscribe Pro/Dealer |

## 📊 Market Opportunity

- **$20.9 billion** market (2024) → **$47.5 billion** by 2035 (8.6% CAGR)
- 92% of collectors are 45+, 87% male, 36% earn $100k+
- Estate seller segment is completely unserved by existing platforms
- Reddit coin communities: 900k+ combined members
- No existing platform combines AI grading + active matching + tiered pricing

## 🗺️ Roadmap

- [x] V1 Backend (FastAPI + PostgreSQL + Stripe Connect)
- [x] V1 Frontend (Next.js landing + auth + dashboard)
- [x] Commission engine (tiered 4.5% → 1.0%)
- [x] Want-list builder + matching engine
- [x] Fresh Estate Inventory alerts
- [ ] ML grading model (EfficientNet-B7 / ViT)
- [ ] Reddit/estate scraper agent
- [ ] Collector profile enrichment
- [ ] Mobile app (React Native)

---

**JBAnalytics LLC** | Built with 🤖 by Viktor AI
