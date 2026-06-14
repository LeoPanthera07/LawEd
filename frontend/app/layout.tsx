import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import { Header } from "@/components/shared/Header";
import { Footer } from "@/components/shared/Footer";
import { ErrorBoundary } from "@/components/shared/ErrorBoundary";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "NyayaSetu — Legal Intelligence for Every Citizen",
  description:
    "Get instant legal intelligence grounded in BNS, BNSS & BSA. Describe your situation, receive applicable clauses.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} flex min-h-screen flex-col antialiased`}
      >
        <Header />
        <ErrorBoundary>
          <main className="flex-1">{children}</main>
        </ErrorBoundary>
        <Footer />
      </body>
    </html>
  );
}
