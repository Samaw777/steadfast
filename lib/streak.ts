// Streak counts whole days elapsed since the reference instant (last relapse,
// or account creation if there hasn't been one). A relapse logged "today"
// brings the streak back to 0, not -1 or 1.
export function currentStreakDays(referenceIso: string): number {
  const reference = new Date(referenceIso).getTime();
  const now = Date.now();
  return Math.max(0, Math.floor((now - reference) / 86_400_000));
}

export function streakReference(profile: { last_relapse_at: string | null; created_at: string }): string {
  return profile.last_relapse_at ?? profile.created_at;
}

export function isoDate(d: Date): string {
  return d.toISOString().slice(0, 10);
}

export function todayIso(): string {
  return isoDate(new Date());
}
