export type Verse = { text: string; ref: string };

export const VERSES_GENERAL: Verse[] = [
  { text: "No temptation has overtaken you except what is common to mankind. And God is faithful; he will not let you be tempted beyond what you can bear.", ref: "1 Corinthians 10:13" },
  { text: "I can do all this through him who gives me strength.", ref: "Philippians 4:13" },
  { text: "Come to me, all you who are weary and burdened, and I will give you rest.", ref: "Matthew 11:28" },
  { text: "The Lord is close to the brokenhearted and saves those who are crushed in spirit.", ref: "Psalm 34:18" },
  { text: "Therefore, if anyone is in Christ, the new creation has come: the old has gone, the new is here!", ref: "2 Corinthians 5:17" },
  { text: "Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.", ref: "Joshua 1:9" },
  { text: "Create in me a pure heart, O God, and renew a steadfast spirit within me.", ref: "Psalm 51:10" },
  { text: "But he said to me, \"My grace is sufficient for you, for my power is made perfect in weakness.\"", ref: "2 Corinthians 12:9" },
  { text: "Set your minds on things above, not on earthly things.", ref: "Colossians 3:2" },
  { text: "The Lord is my shepherd, I lack nothing.", ref: "Psalm 23:1" },
];

export const VERSES_TEMPTATION: Verse[] = [
  { text: "No temptation has overtaken you except what is common to mankind. And God is faithful; he will not let you be tempted beyond what you can bear. But when you are tempted, he will also provide a way out so that you can endure it.", ref: "1 Corinthians 10:13" },
  { text: "Submit yourselves, then, to God. Resist the devil, and he will flee from you.", ref: "James 4:7" },
  { text: "Watch and pray so that you will not fall into temptation. The spirit is willing, but the flesh is weak.", ref: "Matthew 26:41" },
  { text: "I have hidden your word in my heart that I might not sin against you.", ref: "Psalm 119:11" },
  { text: "Flee from sexual immorality... Therefore honor God with your bodies.", ref: "1 Corinthians 6:18,20" },
  { text: "Let us throw off everything that hinders and the sin that so easily entangles, and let us run with perseverance the race marked out for us.", ref: "Hebrews 12:1" },
];

export const VERSES_GRACE: Verse[] = [
  { text: "If we confess our sins, he is faithful and just and will forgive us our sins and purify us from all unrighteousness.", ref: "1 John 1:9" },
  { text: "As far as the east is from the west, so far has he removed our transgressions from us.", ref: "Psalm 103:12" },
  { text: "Therefore, there is now no condemnation for those who are in Christ Jesus.", ref: "Romans 8:1" },
  { text: "The steadfast love of the Lord never ceases, his mercies never come to an end; they are new every morning.", ref: "Lamentations 3:22-23" },
];

function dayOfYear(): number {
  const start = new Date(new Date().getFullYear(), 0, 0);
  return Math.floor((Date.now() - start.getTime()) / 86_400_000);
}

export function verseOfTheDay(): Verse {
  return VERSES_GENERAL[dayOfYear() % VERSES_GENERAL.length];
}

export function randomVerse(list: Verse[]): Verse {
  return list[Math.floor(Math.random() * list.length)];
}
