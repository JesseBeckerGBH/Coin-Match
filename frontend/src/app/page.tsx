'use client';

import Link from 'next/link';

export default function Home() {
  return (
    <main className="min-h-screen bg-gradient-to-b from-navy-500 via-navy-600 to-navy-800">
      {/* Nav */}
      <nav className="flex items-center justify-between px-8 py-4 max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <span className="text-3xl">🪙</span>
          <span className="text-gold-400 text-2xl font-bold tracking-tight">CoinMatch</span>
        </div>
        <div className="flex items-center gap-4">
          <a href="/auth/login" className="text-gold-200 hover:text-gold-400 transition-colors">
            Log In
          </a>
          <a href="/auth/signup" className="btn-primary text-sm">
            Get Started Free
          </a>
        </div>
      </nav>

      {/* Hero */}
      <section className="max-w-5xl mx-auto px-8 pt-20 pb-32 text-center">
        <h1 className="text-5xl md:text-7xl font-bold text-white leading-tight mb-6">
          The{' '}
          <span className="text-gold-400">Smartest Way</span>
          <br />
          to Buy &amp; Sell Coins
        </h1>
        <p className="text-xl md:text-2xl text-gold-200/80 max-w-3xl mx-auto mb-10 leading-relaxed">
          AI-powered grading. Instant buyer matching. The lowest fees in numismatics —
          as low as <strong className="text-gold-400">1%</strong> on big sales.
          Heritage charges 25-35%. We don&apos;t.
        </p>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <a
            href="/auth/signup?type=buyer"
            className="btn-primary text-lg px-8 py-4 inline-block"
          >
            🔍 I&apos;m a Collector
          </a>
          <a
            href="/auth/signup?type=estate_seller"
            className="btn-secondary text-lg px-8 py-4 inline-block"
          >
            🏠 I Inherited Coins
          </a>
        </div>
        <p className="mt-4 text-sm text-gold-200/50">
          Estate sellers pay zero subscription — commission only on successful sale
        </p>
      </section>

      {/* How It Works */}
      <section className="bg-white py-20">
        <div className="max-w-6xl mx-auto px-8">
          <h2 className="text-4xl font-bold text-navy-500 text-center mb-16">
            How CoinMatch Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: '📸',
                title: 'Upload Photos',
                desc: 'Snap 2-4 photos of your coin. Our AI needs obverse, reverse, and optionally edge + detail shots.',
              },
              {
                icon: '🤖',
                title: 'AI Grades Instantly',
                desc: 'Get a Sheldon scale grade (1-70), confidence score, luster rating, and estimated market value — in seconds.',
              },
              {
                icon: '🎯',
                title: 'Get Matched',
                desc: 'Our engine matches your coin with verified buyers whose want-lists match. Pro members get first access.',
              },
            ].map((step, i) => (
              <div key={i} className="card text-center">
                <div className="text-5xl mb-4">{step.icon}</div>
                <h3 className="text-xl font-bold text-navy-500 mb-3">{step.title}</h3>
                <p className="text-navy-300 leading-relaxed">{step.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Fee Comparison */}
      <section className="bg-gold-50 py-20">
        <div className="max-w-5xl mx-auto px-8">
          <h2 className="text-4xl font-bold text-navy-500 text-center mb-4">
            Keep More of What Your Coins Are Worth
          </h2>
          <p className="text-center text-navy-300 mb-12 text-lg">
            On a $100,000 collection sale:
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="card text-center border-red-200 bg-red-50">
              <h3 className="font-bold text-red-700 text-lg mb-2">Heritage Auctions</h3>
              <p className="text-4xl font-bold text-red-600 mb-1">$15,000</p>
              <p className="text-red-400">in fees (15%)</p>
              <p className="text-sm text-red-300 mt-2">Seller gets: $85,000</p>
            </div>
            <div className="card text-center border-orange-200 bg-orange-50">
              <h3 className="font-bold text-orange-700 text-lg mb-2">Local Dealer</h3>
              <p className="text-4xl font-bold text-orange-600 mb-1">$25,000</p>
              <p className="text-orange-400">in markup (25%)</p>
              <p className="text-sm text-orange-300 mt-2">Seller gets: $75,000</p>
            </div>
            <div className="card text-center border-green-300 bg-green-50 ring-2 ring-green-400">
              <h3 className="font-bold text-green-700 text-lg mb-2">CoinMatch ✨</h3>
              <p className="text-4xl font-bold text-green-600 mb-1">$1,000</p>
              <p className="text-green-500">in fees (1%)</p>
              <p className="text-sm text-green-600 mt-2 font-bold">Seller gets: $99,000</p>
            </div>
          </div>
        </div>
      </section>

      {/* Fresh Inventory */}
      <section className="bg-navy-500 py-20">
        <div className="max-w-4xl mx-auto px-8 text-center">
          <div className="text-6xl mb-6">🪙</div>
          <h2 className="text-4xl font-bold text-gold-400 mb-6">
            Fresh Estate Inventory Alerts
          </h2>
          <p className="text-xl text-gold-200/80 mb-8 leading-relaxed max-w-2xl mx-auto">
            When someone inherits a coin collection, you&apos;re the first to know.
            Pro and Dealer members get 24-hour early access to new estate listings
            before they hit the public marketplace.
          </p>
          <a href="/auth/signup?type=buyer" className="btn-primary text-lg px-8 py-4 inline-block">
            Get Early Access →
          </a>
        </div>
      </section>

      {/* Pricing */}
      <section className="bg-white py-20">
        <div className="max-w-6xl mx-auto px-8">
          <h2 className="text-4xl font-bold text-navy-500 text-center mb-16">
            Simple, Transparent Pricing
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="card text-center">
              <h3 className="text-xl font-bold text-navy-500 mb-2">Free Buyer</h3>
              <p className="text-4xl font-bold text-navy-500 mb-1">$0</p>
              <p className="text-navy-300 mb-6">per month</p>
              <ul className="text-left text-navy-400 space-y-2 mb-6">
                <li>✅ Browse all listings</li>
                <li>✅ 5 want-list items</li>
                <li>✅ 3% buyer commission</li>
                <li>❌ No early estate access</li>
              </ul>
              <a href="/auth/signup" className="btn-secondary text-sm w-full inline-block">
                Sign Up Free
              </a>
            </div>
            <div className="card text-center ring-2 ring-gold-400 relative">
              <div className="absolute -top-3 left-1/2 -translate-x-1/2 bg-gold-400 text-navy-500 text-xs font-bold px-3 py-1 rounded-full">
                MOST POPULAR
              </div>
              <h3 className="text-xl font-bold text-navy-500 mb-2">Pro Collector</h3>
              <p className="text-4xl font-bold text-gold-500 mb-1">$19</p>
              <p className="text-navy-300 mb-6">per month</p>
              <ul className="text-left text-navy-400 space-y-2 mb-6">
                <li>✅ 24h early estate access</li>
                <li>✅ Unlimited want-list items</li>
                <li>✅ 1.5% buyer commission</li>
                <li>✅ Price history &amp; trends</li>
                <li>✅ Priority matching</li>
              </ul>
              <a href="/auth/signup?tier=pro" className="btn-primary text-sm w-full inline-block">
                Start Pro Trial
              </a>
            </div>
            <div className="card text-center">
              <h3 className="text-xl font-bold text-navy-500 mb-2">Dealer</h3>
              <p className="text-4xl font-bold text-navy-500 mb-1">$99</p>
              <p className="text-navy-300 mb-6">per month</p>
              <ul className="text-left text-navy-400 space-y-2 mb-6">
                <li>✅ Instant estate alerts</li>
                <li>✅ Unlimited everything</li>
                <li>✅ 0.75% buyer commission</li>
                <li>✅ API access</li>
                <li>✅ Batch listing tools</li>
                <li>✅ Analytics dashboard</li>
              </ul>
              <a href="/auth/signup?tier=dealer" className="btn-secondary text-sm w-full inline-block">
                Go Dealer
              </a>
            </div>
          </div>
          <p className="text-center text-navy-300 mt-8">
            Estate sellers always free — pay only a small commission on successful sales (as low as 1% on $50k+ coins, $10 minimum)
          </p>
        </div>
      </section>

      {/* Estate Seller CTA */}
      <section className="bg-gold-50 py-20">
        <div className="max-w-3xl mx-auto px-8 text-center">
          <h2 className="text-4xl font-bold text-navy-500 mb-6">
            Inherited a Coin Collection?
          </h2>
          <p className="text-xl text-navy-400 mb-8 leading-relaxed">
            Don&apos;t let a dealer pay you 40 cents on the dollar. Upload photos,
            get an instant AI grade, and connect directly with verified collectors
            who will pay fair market value. No subscription — ever.
          </p>
          <a
            href="/auth/signup?type=estate_seller"
            className="btn-primary text-lg px-8 py-4 inline-block"
          >
            Get a Free Assessment →
          </a>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-navy-800 text-gold-200/60 py-12">
        <div className="max-w-6xl mx-auto px-8 flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-2">
            <span className="text-xl">🪙</span>
            <span className="text-gold-400 font-bold">CoinMatch</span>
            <span className="text-sm ml-2">by JBAnalytics LLC</span>
          </div>
          <div className="flex gap-6 text-sm">
            <a href="/pricing" className="hover:text-gold-400">Pricing</a>
            <a href="/about" className="hover:text-gold-400">About</a>
            <a href="/docs" className="hover:text-gold-400">API</a>
            <a href="/privacy" className="hover:text-gold-400">Privacy</a>
            <a href="/terms" className="hover:text-gold-400">Terms</a>
          </div>
          <p className="text-xs">© 2026 JBAnalytics LLC. All rights reserved.</p>
        </div>
      </footer>
    </main>
  );
}
