export type Profile = {
  id: string;
  name: string;
  last_relapse_at: string | null;
  longest_streak_days: number;
  created_at: string;
};

export type CheckinStatus = "clean" | "relapse";

export type Checkin = {
  id: string;
  user_id: string;
  day: string; // yyyy-mm-dd
  status: CheckinStatus;
  mood: number | null; // 1-5
  note: string | null;
  created_at: string;
};

export type UrgeOutcome = "resisted" | "relapsed";

export type UrgeLog = {
  id: string;
  user_id: string;
  outcome: UrgeOutcome;
  note: string | null;
  created_at: string;
};
