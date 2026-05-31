# CoinMatch Maintenance & Deployment Guide

## 🚀 Deployment Instructions

### 1. Railway Deployment
- Push this repository to GitHub.
- Link your GitHub repo to a new project in [Railway](https://railway.app/).
- Add the required environment variables from `README.md` (DATABASE_URL, JWT_SECRET, STRIPE_SECRET_KEY, etc.).
- Railway will automatically detect the `railway.toml` and deploy the services.

### 2. Stripe Connect setup
- Create a [Stripe](https://stripe.com/) account.
- Enable **Stripe Connect** (Express accounts).
- In your Stripe Dashboard, go to **Settings > External Accounts** (or Bank Accounts).
- Link your **Mercury Bank** account using the routing and account numbers provided by Mercury.
- Funds will flow from the buyer → Stripe → Your Mercury account (platform fee) and the Seller's account (coin price minus fee).

### 3. Domain Setup
- Your domain `getcoinmatch.com` is registered via Cloudflare.
- Point the `A` or `CNAME` records in Cloudflare to your Railway app's public URL.

## 🤖 AI & Scraper Maintenance

### AI Grading Engine (V2)
- The grader in `engine/grading/grader.py` is structured for Multimodal Vision. 
- To use live Gemini 1.5 Pro analysis, integrate the `google-generativeai` library and pass images to the model with a prompt focusing on "luster," "strike," and "surface wear."

### Reddit Scraper
- The scraper lives in `engine/scraping/reddit_scraper.py`.
- Run it periodically as a Celery task or a standalone cron job.
- It will automatically identify potential estate sellers on Reddit and log them to the `estate_events` table for outreach.

## 💰 Commission Model
- **Note:** Per your request, the commission percentage **increases** as the sale value increases:
  - $0-$500: 1.0%
  - $50k+: 5.0%
- This is defined in `backend/app/services/commission.py`.

## 📈 Collector Profiles
- Profiles are enriched with `user_type`, `age_bracket`, and `collecting_focus`.
- Use the `/api/auth/me` or `/api/users/{id}` endpoints to access and personalize marketing content based on these fields.

---

**JBAnalytics LLC** | Finalized by Gemini CLI 🤖
