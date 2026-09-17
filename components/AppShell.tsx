"use client";

import { usePathname } from "next/navigation";
import { useUser } from "./UserProvider";
import { AuthGate } from "./AuthGate";
import { Nav } from "./Nav";

export function AppShell({ children }: { children: React.ReactNode }) {
  const { profile, loading } = useUser();
  const pathname = usePathname();

  // Recovery links land here with their own transient auth state, before a
  // normal session/profile exists — this route manages its own full-screen UI.
  if (pathname === "/reset-password") {
    return <>{children}</>;
  }

  if (loading) {
    return <div className="min-h-screen w-full bg-bg" />;
  }

  if (!profile) {
    return <AuthGate />;
  }

  return (
    <div className="w-full min-h-screen bg-bg text-text flex flex-col md:flex-row">
      <Nav />
      <main className="flex-1 p-4 pb-24 md:p-8 max-w-3xl">{children}</main>
    </div>
  );
}
