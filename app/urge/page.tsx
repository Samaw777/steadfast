"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Check } from "lucide-react";
import { useUser } from "@/components/UserProvider";
import { PageHeader, Panel, VerseBlock } from "@/components/Ui";
import { logRelapse, logUrge } from "@/lib/actions";
import { randomVerse, VERSES_TEMPTATION } from "@/lib/verses";

const DISTRACTIONS = [
  "Step outside for a few minutes, even just to a doorway or balcony.",
  "Call or text someone you trust — you don't have to explain why.",
  "Do 20 push-ups or go for a brisk walk.",
  "Put on music and change the room you're in.",
  "Write down what you're feeling right now, in one sentence.",
  "Splash cold water on your face.",
  "Pick up a book or podcast you've been meaning to get to.",
];

export default function UrgePage() {
  const { profile, setProfile } = useUser();
  const router = useRouter();

  // Lazy initializers run once at mount, not on every render, so picking
  // randomly here doesn't violate the render-purity rule the way useMemo would.
  const [verse] = useState(() => randomVerse(VERSES_TEMPTATION));
  const [distraction] = useState(() => DISTRACTIONS[Math.floor(Math.random() * DISTRACTIONS.length)]);

  const [confirmingRelapse, setConfirmingRelapse] = useState(false);
  const [busy, setBusy] = useState(false);
  const [resolved, setResolved] = useState<"resisted" | "relapsed" | null>(null);

  async function handleResisted() {
    if (!profile || busy) return;
    setBusy(true);
    await logUrge(profile.id, "resisted", null);
    setBusy(false);
    setResolved("resisted");
  }

  async function handleRelapsed() {
    if (!profile || busy) return;
    if (!confirmingRelapse) {
      setConfirmingRelapse(true);
      return;
    }
    setBusy(true);
    await logUrge(profile.id, "relapsed", null);
    const updated = await logRelapse(profile);
    if (updated) setProfile(updated);
    setBusy(false);
    setResolved("relapsed");
  }

  if (resolved) {
    return (
      <div className="flex flex-col items-center justify-center text-center min-h-[60vh]">
        <Check size={32} className="text-accent mb-4" />
        <p className="text-lg mb-2" style={{ fontFamily: "var(--font-head)" }}>
          {resolved === "resisted" ? "That took strength. Well done." : "Tomorrow is a new day."}
        </p>
        <p className="text-sm text-muted mb-6 max-w-xs">
          {resolved === "resisted"
            ? "This moment is logged. Every time you get through one of these, it gets a little easier."
            : "Your longest streak is saved. Log today's check-in when you're ready and start again."}
        </p>
        <button onClick={() => router.push("/")} className="text-sm text-accent hover:underline">
          Back to home
        </button>
      </div>
    );
  }

  return (
    <div>
      <PageHeader eyebrow="Right now" title="You can get through this" />

      <div className="bg-panel border border-border rounded-lg p-8 flex flex-col items-center mb-6">
        <div className="breathe-circle w-28 h-28 rounded-full mb-4" style={{ background: "var(--accent)" }} />
        <p className="text-sm text-muted text-center">
          Breathe in slowly as the circle grows, breathe out as it shrinks. Keep going for a minute.
        </p>
      </div>

      <Panel title="Try this">
        <p className="text-sm leading-relaxed">{distraction}</p>
      </Panel>

      <div className="my-6">
        <Panel title="Hold on to this">
          <VerseBlock text={verse.text} reference={verse.ref} />
        </Panel>
      </div>

      {confirmingRelapse && (
        <p className="text-sm text-danger mb-3 text-center">
          Tap again to confirm — this logs today as a slip and resets your streak.
        </p>
      )}

      <div className="flex gap-3">
        <button
          onClick={handleResisted}
          disabled={busy}
          className="flex-1 py-3 bg-accent text-[#06120d] font-medium rounded-md hover:opacity-90 transition-opacity disabled:opacity-60"
        >
          I&apos;m okay now
        </button>
        <button
          onClick={handleRelapsed}
          disabled={busy}
          className="flex-1 py-3 border border-border text-muted rounded-md hover:border-danger hover:text-danger transition-colors disabled:opacity-60"
        >
          I slipped
        </button>
      </div>
    </div>
  );
}
