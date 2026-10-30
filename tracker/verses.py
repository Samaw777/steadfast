from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Verse:
    text: str
    ref: str


GENERAL = [
    Verse("No temptation has overtaken you except what is common to mankind. And God is faithful; he will not let you be tempted beyond what you can bear.", "1 Corinthians 10:13"),
    Verse("I can do all this through him who gives me strength.", "Philippians 4:13"),
    Verse("Come to me, all you who are weary and burdened, and I will give you rest.", "Matthew 11:28"),
    Verse("The Lord is close to the brokenhearted and saves those who are crushed in spirit.", "Psalm 34:18"),
    Verse("Therefore, if anyone is in Christ, the new creation has come: the old has gone, the new is here!", "2 Corinthians 5:17"),
    Verse("Be strong and courageous. Do not be afraid; do not be discouraged, for the Lord your God will be with you wherever you go.", "Joshua 1:9"),
    Verse("Create in me a pure heart, O God, and renew a steadfast spirit within me.", "Psalm 51:10"),
    Verse('But he said to me, "My grace is sufficient for you, for my power is made perfect in weakness."', "2 Corinthians 12:9"),
    Verse("Set your minds on things above, not on earthly things.", "Colossians 3:2"),
    Verse("The Lord is my shepherd, I lack nothing.", "Psalm 23:1"),
]

GRACE = [
    Verse("If we confess our sins, he is faithful and just and will forgive us our sins and purify us from all unrighteousness.", "1 John 1:9"),
    Verse("As far as the east is from the west, so far has he removed our transgressions from us.", "Psalm 103:12"),
    Verse("Therefore, there is now no condemnation for those who are in Christ Jesus.", "Romans 8:1"),
    Verse("The steadfast love of the Lord never ceases, his mercies never come to an end; they are new every morning.", "Lamentations 3:22-23"),
]


def verse_of_the_day(today: date) -> Verse:
    return GENERAL[today.timetuple().tm_yday % len(GENERAL)]
