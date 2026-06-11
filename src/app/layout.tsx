import type { Metadata } from "next";
import localFont from "next/font/local";
import type { ReactNode } from "react";
import "./globals.css";

// Variable cuts carry wght 300-800 and wdth 75-100, so the condensed family
// is the same font: pair `font-condensed` with `font-stretch-condensed`.
const openSans = localFont({
  src: [
    {
      path: "../../public/fonts/OpenSans-Variable-Regular.ttf",
      style: "normal",
    },
    {
      path: "../../public/fonts/OpenSans-Variable-Italic.ttf",
      style: "italic",
    },
  ],
  variable: "--font-open-sans",
  weight: "300 800",
  display: "swap",
});

export const metadata: Metadata = {
  title: "iCPMG Workbench • Alpha",
  description: "KPMG's candidate intelligence layer for iCIMS.",
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html className={openSans.variable} lang="en">
      <body>{children}</body>
    </html>
  );
}
