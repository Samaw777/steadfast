"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { LifeBuoy, NotebookPen, CheckCircle2 } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { useUser } from "@/components/UserProvider";
import { PageHeader, Panel, StatCard, VerseBlock } from "@/components/Ui";
import { currentStreakDays, streakReference, todayIso } from "@/lib/streak";
import { verseOfTheDay } from "@/lib/verses";

function greeting() {
  const hour = new Date().getHours();
  if (hour < 12) return "Good morning";
  if (hour < 18) return "Good afternoon";
  return "Good evening";
}

export default function HomePage() {
  const { profile } = useUser();
  const verse = verseOfTheDay();

  const [weekCheckins, setWeekCheckins] = useState(0);
  const [checkedInToday, setCheckedInToday] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!profile) return;
    let cancelled = false;

    async function load() {
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);

      const [week, today] = await Promise.all([
        supabase
          .from("checkins")
          .select("id")
          .eq("user_id", profile!.id)
          .gte("day", weekAgo.toISOString().slice(0, 10)),
        supabase.from("checkins").select("id").eq("user_id", profile!.id).eq("day", todayIso()).maybeSingle(),
      ]);

      if (cancelled) return;
      setWeekCheckins((week.data ?? []).length);
      setCheckedInToday(!!today.data);
      setLoading(false);
    }
    load();
    return () => {
      cancelled = true;
    };
  }, [profile]);

  if (!profile) return null;

  const streak = currentStreakDays(streakReference(profile));

  return (
    <div>
      <PageHeader eyebrow={greeting()} title={profile.name} />

      <div className="bg-panel border border-border rounded-lg p-8 text-center mb-6">
        <p className="text-xs uppercase tracking-wide text-muted mb-2">Current streak</p>
        <p className="text-6xl mb-2" style={{ fontFamily: "var(--font-head)" }}>
          {streak}
        </p>
        <p className="text-sm text-muted">{streak === 1 ? "day steady" : "days steady"}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 mb-6">
        <StatCard label="Longest streak" value={`${profile.longest_streak_days}`} sub="days, so far" />
        <StatCard label="Check-ins" value={`${loading ? "—" : weekCheckins}`} sub="in the last 7 days" />
      </div>

      <div className="grid gap-4 mb-6 sm:grid-cols-2">
        <Link
          href="/checkin"
          className="flex items-center gap-3 bg-panel border border-border rounded-lg p-5 hover:border-muted transition-colors"
        >
          {checkedInToday ? (
            <CheckCircle2 className="text-ok shrink-0" size={22} />
          ) : (
            <NotebookPen className="text-accent shrink-0" size={22} />
          )}
          <div>
            <p className="text-sm">{checkedInToday ? "Today's check-in is done" : "Check in for today"}</p>
            <p className="text-xs text-muted">{checkedInToday ? "You can still edit it" : "Takes less than a minute"}</p>
          </div>
        </Link>

        <Link
          href="/urge"
          className="flex items-center gap-3 bg-panel border border-border rounded-lg p-5 hover:border-muted transition-colors"
        >
          <LifeBuoy className="text-warn shrink-0" size={22} />
          <div>
            <p className="text-sm">Feeling an urge right now?</p>
            <p className="text-xs text-muted">Open the urge tool</p>
          </div>
        </Link>
      </div>

      <Panel title="Verse for today">
        <VerseBlock text={verse.text} reference={verse.ref} />
      </Panel>
    </div>
  );
}
