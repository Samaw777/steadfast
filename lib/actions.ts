import { supabase } from "@/lib/supabase";
import { currentStreakDays, streakReference, todayIso } from "@/lib/streak";
import type { CheckinStatus, Profile } from "@/lib/types";

// Resets the streak clock and banks the streak just ended into longest_streak_days
// if it was a new record. Called whenever a relapse is logged, whether from the
// check-in form or the urge tool.
export async function logRelapse(profile: Profile): Promise<Profile | null> {
  const endedStreak = currentStreakDays(streakReference(profile));
  const longest = Math.max(profile.longest_streak_days, endedStreak);
  const now = new Date().toISOString();

  const { data, error } = await supabase
    .from("profiles")
    .update({ last_relapse_at: now, longest_streak_days: longest })
    .eq("id", profile.id)
    .select()
    .single();

  if (error) {
    console.error("Failed to log relapse:", error);
    return null;
  }
  return data as Profile;
}

export async function upsertTodayCheckin(
  userId: string,
  status: CheckinStatus,
  mood: number | null,
  note: string | null
) {
  return supabase
    .from("checkins")
    .upsert(
      { user_id: userId, day: todayIso(), status, mood, note },
      { onConflict: "user_id,day" }
    )
    .select()
    .single();
}

export async function logUrge(userId: string, outcome: "resisted" | "relapsed", note: string | null) {
  return supabase.from("urge_logs").insert({ user_id: userId, outcome, note }).select().single();
}
