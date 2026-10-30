"""The Bible study reading plan.

Each study is one day: a passage to read, a key verse, a few questions to reflect on,
and a short prayer. Key verses are quoted from the NIV.
"""

from dataclasses import dataclass
from urllib.parse import urlencode


@dataclass(frozen=True)
class Study:
    day: int
    slug: str
    title: str
    passage: str
    key_verse: str
    key_ref: str
    intro: str
    questions: tuple[str, ...]
    prayer: str

    @property
    def read_url(self):
        return "https://www.biblegateway.com/passage/?" + urlencode({"search": self.passage, "version": "NIV"})


PLAN_TITLE = "Built on the Rock"
PLAN_SUMMARY = "Fourteen days on standing firm, growing in grace, and being renewed from the inside out."

STUDIES = [
    Study(
        1, "built-on-the-rock", "Built on the rock", "Matthew 7:24-27",
        "Therefore everyone who hears these words of mine and puts them into practice is like a wise man who built his house on the rock.",
        "Matthew 7:24",
        "Jesus ends the Sermon on the Mount with a picture of two houses. Both face the same storm; only the foundation is different.",
        (
            "What storms are you facing in this season of life?",
            "What does it look like, practically, to put Jesus' words into practice this week?",
            "Where are you tempted to build on sand: busyness, approval, comfort?",
        ),
        "Lord, be the foundation under everything I build. Teach me not only to hear your words, but to live them.",
    ),
    Study(
        2, "abide-in-the-vine", "Remain in the vine", "John 15:1-11",
        "I am the vine; you are the branches. If you remain in me and I in you, you will bear much fruit; apart from me you can do nothing.",
        "John 15:5",
        "A branch doesn't strain to produce fruit. It stays connected, and life flows through it.",
        (
            "What helps you stay connected to Jesus day to day?",
            "Where are you trying to bear fruit in your own strength?",
            "What might God be pruning in your life right now, and why?",
        ),
        "Jesus, I want to remain in you. Draw me close today, and let your life flow through mine.",
    ),
    Study(
        3, "a-new-creation", "A new creation", "2 Corinthians 5:14-21",
        "Therefore, if anyone is in Christ, the new creation has come: the old has gone, the new is here!",
        "2 Corinthians 5:17",
        "Paul doesn't say we are improved versions of ourselves. In Christ, something genuinely new has begun.",
        (
            "What \"old\" things do you still carry as if they define you?",
            "How would you describe yourself if you fully believed this verse?",
            "Who in your life needs to hear the message of reconciliation?",
        ),
        "Father, thank you that in Christ I am new. Help me live from who you say I am, not who I used to be.",
    ),
    Study(
        4, "no-condemnation", "No condemnation", "Romans 8:1-11",
        "Therefore, there is now no condemnation for those who are in Christ Jesus.",
        "Romans 8:1",
        "Romans 8 opens with a verdict. Before anything is asked of us, the sentence has already been lifted.",
        (
            "Where do you still hear a voice of condemnation?",
            "What is the difference between conviction and condemnation?",
            "How does setting your mind on the Spirit change your day?",
        ),
        "Thank you, Jesus, that there is no condemnation for me in you. Quiet every accusing voice with your truth.",
    ),
    Study(
        5, "renewing-the-mind", "Renewing the mind", "Romans 12:1-2",
        "Do not conform to the pattern of this world, but be transformed by the renewing of your mind. Then you will be able to test and approve what God's will is—his good, pleasing and perfect will.",
        "Romans 12:2",
        "Transformation begins in the mind. What we let shape our thinking will shape our lives.",
        (
            "What patterns of this world shape your thinking the most?",
            "What could you feed your mind with more often this week?",
            "What would offering yourself as a living sacrifice look like today?",
        ),
        "God, renew my mind. Reshape what I think about, what I want, and how I see the world.",
    ),
    Study(
        6, "the-way-out", "A way out", "1 Corinthians 10:12-13",
        "No temptation has overtaken you except what is common to mankind. And God is faithful; he will not let you be tempted beyond what you can bear. But when you are tempted, he will also provide a way out so that you can endure it.",
        "1 Corinthians 10:13",
        "You are not the only one, and you are not without help. God's faithfulness meets us in the hard moments.",
        (
            "Why does it matter that our struggles are \"common to mankind\"?",
            "Think of a time God provided a way out. What did it look like?",
            "What \"ways out\" can you prepare ahead of time?",
        ),
        "Faithful God, thank you that I am never without a way through. Open my eyes to it when I need it most.",
    ),
    Study(
        7, "strength-in-weakness", "Strength in weakness", "2 Corinthians 12:7-10",
        "But he said to me, \"My grace is sufficient for you, for my power is made perfect in weakness.\"",
        "2 Corinthians 12:9",
        "Paul asked three times for his thorn to be removed. God's answer was grace instead.",
        (
            "What weakness do you most wish God would simply take away?",
            "How have you seen God's power show up when you felt weak?",
            "What would it mean to \"boast\" in your weaknesses?",
        ),
        "Lord, your grace is enough for me today. Show your strength in the places where I fall short.",
    ),
    Study(
        8, "run-the-race", "Run the race", "Hebrews 12:1-3",
        "Let us throw off everything that hinders and the sin that so easily entangles, and let us run with perseverance the race marked out for us.",
        "Hebrews 12:1",
        "The Christian life is a long-distance race, run with others cheering, and with eyes fixed on Jesus.",
        (
            "What hinders you, even if it isn't wrong in itself?",
            "Who is in your \"great cloud of witnesses\"?",
            "How does fixing your eyes on Jesus help you keep going?",
        ),
        "Jesus, help me lay down what slows me down, and keep my eyes on you for the whole race.",
    ),
    Study(
        9, "fruit-of-the-spirit", "The fruit of the Spirit", "Galatians 5:16-25",
        "But the fruit of the Spirit is love, joy, peace, forbearance, kindness, goodness, faithfulness, gentleness and self-control. Against such things there is no law.",
        "Galatians 5:22-23",
        "Fruit grows slowly and naturally. These qualities are the Spirit's work in us, not a checklist to perform.",
        (
            "Which fruit do you see growing in your life lately?",
            "Which one do you most long for God to grow in you?",
            "What does \"keeping in step with the Spirit\" look like in your daily routine?",
        ),
        "Holy Spirit, grow your fruit in me. Make me more loving, more patient, and more like Jesus.",
    ),
    Study(
        10, "every-thought-captive", "Every thought captive", "2 Corinthians 10:3-5",
        "We demolish arguments and every pretension that sets itself up against the knowledge of God, and we take captive every thought to make it obedient to Christ.",
        "2 Corinthians 10:5",
        "Many battles are won or lost in our thoughts. We don't have to believe every thought we think.",
        (
            "What recurring thoughts pull you away from God's truth?",
            "What truth from Scripture answers those thoughts?",
            "What would taking a thought captive look like in the moment?",
        ),
        "Lord, I bring my thoughts to you. Help me recognise lies and replace them with your truth.",
    ),
    Study(
        11, "whatever-is-true", "Whatever is true", "Philippians 4:4-9",
        "Finally, brothers and sisters, whatever is true, whatever is noble, whatever is right, whatever is pure, whatever is lovely, whatever is admirable—if anything is excellent or praiseworthy—think about such things.",
        "Philippians 4:8",
        "Paul links what we dwell on with the peace of God guarding our hearts.",
        (
            "What have you been dwelling on most this week?",
            "Name three things that are true, lovely, or praiseworthy in your life right now.",
            "What anxiety can you turn into prayer today?",
        ),
        "God of peace, guard my heart and mind. Turn my attention to what is good, true, and lovely.",
    ),
    Study(
        12, "two-are-better", "Two are better than one", "Ecclesiastes 4:9-12",
        "Two are better than one, because they have a good return for their labor: If either of them falls down, one can help the other up.",
        "Ecclesiastes 4:9-10",
        "We were never meant to walk alone. Faith grows best in friendship.",
        (
            "Who helps you up when you fall?",
            "Who could you reach out to and encourage this week?",
            "What makes it hard to let others in, and what would help?",
        ),
        "Father, thank you for the people you've placed around me. Give me courage to walk closely with them.",
    ),
    Study(
        13, "new-every-morning", "New every morning", "Lamentations 3:19-26",
        "Because of the Lord's great love we are not consumed, for his compassions never fail. They are new every morning; great is your faithfulness.",
        "Lamentations 3:22-23",
        "Written in the middle of great loss, these verses hold on to hope: each day begins with fresh mercy.",
        (
            "What do you need God's fresh mercy for today?",
            "How have you seen God's faithfulness in a hard season?",
            "What does it mean to \"wait quietly\" for the Lord?",
        ),
        "Lord, thank you that your mercies are new this morning. I receive them, and I trust your faithfulness.",
    ),
    Study(
        14, "a-good-work", "He will finish it", "Philippians 1:3-11",
        "Being confident of this, that he who began a good work in you will carry it on to completion until the day of Christ Jesus.",
        "Philippians 1:6",
        "Your growth doesn't rest on your effort alone. The God who started this work is committed to finishing it.",
        (
            "Looking back over these two weeks, what has God shown you?",
            "Where have you grown, even a little?",
            "What do you want to keep practising from here?",
        ),
        "Thank you, God, that you finish what you start. Carry on your good work in me, one day at a time.",
    ),
]

BY_SLUG = {study.slug: study for study in STUDIES}
