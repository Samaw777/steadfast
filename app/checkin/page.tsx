"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Check } from "lucide-react";
import { supabase } from "@/lib/supabase";
import { useUser } from "@/components/UserProvider";
import { PageHeader, Panel } from "@/components/Ui";
import { logRelapse, upsertTodayCheckin } from "@/lib/actions";
import { todayIso } from "@/lib/streak";
import type { Checkin, CheckinStatus } from "@/lib/types";

const MOODS = [
  { value: 1, label: "Struggling" },
  { value: 2, label: "Low" },
  { value: 3, label: "Okay" },
  { value: 4, label: "Good" },
  { value: 5, label: "Great" },
];

export default function CheckinPage() {
  const { profile, setProfile } = useUser();
  const router = useRouter();

  const [status, setStatus] = useState<CheckinStatus>("clean");
  const [mood, setMood] = useState<number | null>(null);
  const [note, setNote] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [confirmingRelapse, setConfirmingRelapse] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (!profile) return;
    let cancelled = false;
    supabase
      .from("checkins")
      .select("*")
      .eq("user_id", profile.id)
      .eq("day", todayIso())
      .maybeSingle()
      .then(({ data }) => {
        if (cancelled) return;
        const existing = data as Checkin | null;
        if (existing) {
          setStatus(existing.status);
          setMood(existing.mood);
          setNote(existing.note ?? "");
        }
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [profile]);

  async function handleSubmit() {
    if (!profile || saving) return;

    if (status === "relapse" && !confirmingRelapse) {
      setConfirmingRelapse(true);
      return;
    }

    setSaving(true);
    const { error } = await upsertTodayCheckin(profile.id, status, mood, note.trim() || null);
    if (!error && status === "relapse") {
      const updated = await logRelapse(profile);
      if (updated) setProfile(updated);
    }
    setSaving(false);
    if (!error) {
      setSaved(true);
      setTimeout(() => router.push("/"), 900);
    }
  }

  if (loading) return null;

  return (
    <div>
      <PageHeader eyebrow={todayIso()} title="Daily check-in" />

      <Panel title="How did today go?">
        <div className="flex gap-2 mb-5">
          {(["clean", "relapse"] as CheckinStatus[]).map((s) => (
            <button
              key={s}
              onClick={() => {
                setStatus(s);
                setConfirmingRelapse(false);
              }}
              className="flex-1 py-3 rounded-md border text-sm transition-colors"
              style={{
                borderColor: status === s ? (s === "clean" ? "var(--ok)" : "var(--danger)") : "var(--border)",
                background: status === s ? "var(--panel-2)" : "transparent",
                color: status === s ? "var(--text)" : "var(--muted)",
              }}
            >
              {s === "clean" ? "I stayed steady" : "I slipped"}
            </button>
          ))}
        </div>

        <p className="text-xs uppercase tracking-wide text-muted mb-2">Mood</p>
        <div className="flex gap-2 mb-5">
          {MOODS.map((m) => (
            <button
              key={m.value}
              onClick={() => setMood(m.value)}
              title={m.label}
              className="flex-1 py-2 rounded-md border text-xs transition-colors"
              style={{
                borderColor: mood === m.value ? "var(--accent)" : "var(--border)",
                background: mood === m.value ? "var(--panel-2)" : "transparent",
                color: mood === m.value ? "var(--text)" : "var(--muted)",
              }}
            >
              {m.value}
            </button>
          ))}
        </div>

        <p className="text-xs uppercase tracking-wide text-muted mb-2">Notes (optional)</p>
        <textarea
          value={note}
          onChange={(e) => setNote(e.target.value)}
          placeholder="What happened today? Any triggers, wins, or things on your mind."
          rows={4}
          className="w-full bg-panel-2 border border-border px-4 py-3 text-text placeholder-muted-2 outline-none focus:border-accent rounded-md mb-4 resize-none"
        />

        {confirmingRelapse && (
          <p className="text-sm text-danger mb-4">
            This will reset your streak counter. Your longest streak stays saved. Tap &ldquo;Save check-in&rdquo; again to confirm.
          </p>
        )}

        <button
          onClick={handleSubmit}
          disabled={saving}
          className="w-full py-3 bg-accent text-[#06120d] font-medium flex items-center justify-center gap-2 hover:opacity-90 transition-opacity disabled:opacity-60 rounded-md"
        >
          {saved ? (
            <>
              <Check size={16} /> Saved
            </>
          ) : saving ? (
            "Saving…"
          ) : confirmingRelapse ? (
            "Confirm and save check-in"
          ) : (
            "Save check-in"
          )}
        </button>
      </Panel>
    </div>
  );
}
