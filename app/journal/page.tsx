"use client";

import { useEffect, useState } from "react";
import { supabase } from "@/lib/supabase";
import { useUser } from "@/components/UserProvider";
import { PageHeader } from "@/components/Ui";
import type { Checkin } from "@/lib/types";

const MOOD_LABEL: Record<number, string> = {
  1: "Struggling",
  2: "Low",
  3: "Okay",
  4: "Good",
  5: "Great",
};

function formatDay(iso: string) {
  return new Date(`${iso}T00:00:00`).toLocaleDateString(undefined, {
    weekday: "short",
    month: "short",
    day: "numeric",
  });
}

export default function JournalPage() {
  const { profile } = useUser();
  const [entries, setEntries] = useState<Checkin[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profile) return;
    let cancelled = false;
    supabase
      .from("checkins")
      .select("*")
      .eq("user_id", profile.id)
      .order("day", { ascending: false })
      .then(({ data }) => {
        if (cancelled) return;
        setEntries((data as Checkin[]) ?? []);
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [profile]);

  return (
    <div>
      <PageHeader eyebrow="Your history" title="Journal" />

      {loading ? (
        <p className="text-sm text-muted">Loading…</p>
      ) : entries.length === 0 ? (
        <p className="text-sm text-muted">No check-ins yet. Your first one will show up here.</p>
      ) : (
        <div className="flex flex-col gap-3">
          {entries.map((entry) => (
            <div key={entry.id} className="bg-panel border border-border rounded-lg p-4">
              <div className="flex items-center justify-between mb-2">
                <p className="text-sm">{formatDay(entry.day)}</p>
                <span
                  className="text-xs px-2 py-0.5 rounded-full"
                  style={{
                    color: entry.status === "clean" ? "var(--ok)" : "var(--danger)",
                    border: `1px solid ${entry.status === "clean" ? "var(--ok)" : "var(--danger)"}`,
                  }}
                >
                  {entry.status === "clean" ? "Steady" : "Slipped"}
                </span>
              </div>
              {entry.mood && <p className="text-xs text-muted mb-1">Mood: {MOOD_LABEL[entry.mood]}</p>}
              {entry.note && <p className="text-sm text-text/90 leading-relaxed">{entry.note}</p>}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
