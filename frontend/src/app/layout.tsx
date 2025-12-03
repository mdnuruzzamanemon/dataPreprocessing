import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Data Preprocessing Platform',
  description: 'Automatically detect and fix data quality issues in your datasets',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
