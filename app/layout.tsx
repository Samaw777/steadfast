import type { Metadata } from "next";
import "./globals.css";
import { UserProvider } from "@/components/UserProvider";
import { AppShell } from "@/components/AppShell";

export const metadata: Metadata = {
  title: "Steadfast",
  description: "A private space to track your streak, check in daily, and find steadiness when urges hit.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <UserProvider>
          <AppShell>{children}</AppShell>
        </UserProvider>
      </body>
    </html>
  );
}
