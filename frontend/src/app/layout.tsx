import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'CoinMatch by JBAnalytics — AI-Powered Numismatics Marketplace',
  description:
    'Connect with buyers and sellers through AI coin grading and intelligent matching. Lowest fees in the industry. Estate sellers welcome — zero subscription, pay only on sale.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
