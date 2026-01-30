import type { Metadata } from "next";
import { Inter, Merriweather } from "next/font/google";
import "./globals.css";

const inter = Inter({ 
  subsets: ["latin"],
  variable: '--font-inter',
  display: 'swap',
});

const merriweather = Merriweather({ 
  weight: ['300', '400', '700', '900'],
  subsets: ["latin"],
  variable: '--font-merriweather',
  display: 'swap',
});

export const metadata: Metadata = {
  title: "Pandada.AI - Data Wealth Platform",
  description: "Transform raw data into actionable insights with AI-powered analysis",
  viewport: "width=device-width, initial-scale=1",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${merriweather.variable} font-sans`}>
        {children}
      </body>
    </html>
  );
}
