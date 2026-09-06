

EVAL_QUESTIONS = [
    # --- Direct, single-chunk ---
    {
        "question": "What temperature range makes Umbra Cascades produce the sharpest shadow banding?",
        "relevant": [("Umbra Cascades", "Observation Conditions")],
        "expected_answer": "Refraction angles between 8-14 degrees produce the sharpest cascade banding.",
    },
    {
        "question": "What keyword is used to declare variables in Thistle?",
        "relevant": [("The Thistle Programming Language", "Syntax Basics")],
        "expected_answer": "Variables are declared with the `hold` keyword.",
    },
    {
        "question": "Who were the two main signatories of the Meridian Accord?",
        "relevant": [("The Meridian Accord of 1743", "Key Signatories")],
        "expected_answer": "Chancellor Petra Voss of Ostrellan and Doge Alaric Menn of Calvire.",
    },

    # --- Paraphrased (tests semantic retrieval, not keyword match) ---
    {
        "question": "Why can't you use ceramic containers for solar fermentation?",
        "relevant": [("Solar Fermentation", "Ideal Vessel Types")],
        "expected_answer": "Ceramic vessels block the UV wavelengths needed to activate the yeast strain Saccharomyces solis.",
    },
    {
        "question": "How do glimmerfungi spores decide when to start glowing?",
        "relevant": [("Glimmerfungi Phase-Shifting Spores", "Lifecycle")],
        "expected_answer": "Spores switch to the active luminescent phase when ambient humidity crosses 85%.",
    },
    {
        "question": "What's unusual about how a Thistle function handles being reversed?",
        "relevant": [("The Thistle Programming Language", "Design Philosophy")],
        "expected_answer": "Every state change automatically records an inverse operation, so functions can be undone without manual rollback code.",
    },

    # --- Cross-section (answer spans 2 sections of same page) ---
    {
        "question": "What is Cliffball and how did it originally start?",
        "relevant": [("Cliffball", "Rules"), ("Cliffball", "Origins")],
        "expected_answer": "Cliffball is a sport where two teams of five score by landing a disc into tiered levels on a sloped court; it originated among terrace farmers settling irrigation disputes with grain discs.",
    },
    {
        "question": "What is the Tideflow currency system and why is it controversial?",
        "relevant": [("The Tideflow Currency System", "Core Mechanism"), ("The Tideflow Currency System", "Criticisms")],
        "expected_answer": "Tideflow pegs currency value to a rolling average of tidal energy output; critics argue this makes the currency seasonal since tidal output fluctuates with lunar cycles.",
    },
    {
        "question": "What genre is Cobalt Drift and what instrument defines its sound?",
        "relevant": [("Cobalt Drift", "Sound Characteristics"), ("Cobalt Drift", "Notable Instruments")],
        "expected_answer": "Cobalt Drift is a genre built on detuned synth pads and irregular time signatures, heavily featuring the 'strand harp,' a twelve-string instrument played with magnetized picks.",
    },

    # --- Structured content (tables, lists, checklists) ---
    {
        "question": "How many points is the summit tier worth in Cliffball, and what's the rollback penalty?",
        "relevant": [("Cliffball", "Scoring Tiers")],
        "expected_answer": "The summit tier is worth 5 points with a rollback penalty of -2.",
    },
    {
        "question": "What safety steps should you take before starting a solar fermentation batch?",
        "relevant": [("Solar Fermentation", "Safety Checklist")],
        "expected_answer": "Sterilize jars in boiling water for 10 minutes, ensure ambient temperature stays below 38°C during peak sun hours, and discard the batch if mold appears.",
    },
    {
        "question": "What materials do you need to start a solar fermentation batch?",
        "relevant": [("Solar Fermentation", "Required Materials")],
        "expected_answer": "A wide-mouth glass jar (1L+), shredded root vegetable, 3% salt brine, and a breathable cloth cover secured with twine.",
    },

    # --- Distractor / no-answer-in-corpus (tests hallucination resistance) ---
    {
        "question": "What year was Cliffball added to the Olympic Games?",
        "relevant": [],
        "expected_answer": "This information is not present in the notes — Cliffball's Olympic status is never mentioned.",
    },
    {
        "question": "What is the maximum recorded tidal output under the Tideflow system?",
        "relevant": [],
        "expected_answer": "This specific figure is not present in the notes.",
    },

    # --- Direct, more ---
    {
        "question": "What treaty language is quoted from the Meridian Accord?",
        "relevant": [("The Meridian Accord of 1743", "Treaty Excerpt")],
        "expected_answer": "\"Let no vessel of Ostrellan be turned from the waters of Calvire, nor any net cast without leave of the Strait Council.\"",
    },
    {
        "question": "What memory overhead does reversible mutation add in Thistle?",
        "relevant": [("The Thistle Programming Language", "Known Limitations")],
        "expected_answer": "Roughly 15-20% memory overhead per function call.",
    },
        # --- Discrimination questions (added for difficulty) ---
    {
        "question": "What temperature-based method is used to preserve root vegetables outdoors?",
        "relevant": [("Lunar Brining", "Overview")],
        "expected_answer": "Lunar brining uses freeze-thaw cycling overnight, relying on the cold-tolerant yeast strain Saccharomyces lunaris.",
    },
    {
        "question": "Which fermentation technique uses a higher salt concentration, solar fermentation or lunar brining?",
        "relevant": [("Solar Fermentation", "Required Materials"), ("Lunar Brining", "Required Materials")],
        "expected_answer": "Lunar brining uses a 5% salt concentration, higher than solar fermentation's 3%.",
    },
    {
        "question": "What keyword declares a function in Bramble, and how is that different from Thistle?",
        "relevant": [("Bramble", "Syntax Basics")],
        "expected_answer": "Bramble uses `loop` to define functions, compared to Thistle's `weave` keyword.",
    },
    {
        "question": "Which language has higher memory overhead for rollback, Thistle or Bramble?",
        "relevant": [("Bramble", "Known Limitations"), ("The Thistle Programming Language", "Known Limitations")],
        "expected_answer": "Bramble has higher overhead (50-70%) compared to Thistle's reversible mutation approach (15-20%).",
    },
    {
        "question": "What resource is Driftmark currency pegged to?",
        "relevant": [("Driftmark Currency", "Core Mechanism")],
        "expected_answer": "Driftmark is pegged to a rolling average of regional wind energy output.",
    },
    {
        "question": "Which currency system has a longer averaging window, Tideflow or Driftmark?",
        "relevant": [("Driftmark Currency", "Core Mechanism"), ("The Tideflow Currency System", "Criticisms")],
        "expected_answer": "Driftmark uses a 60-day window, longer than Tideflow's original 30-day window.",
    },
    {
        "question": "What's the difference between how Cliffball and Ridgetoss score points?",
        "relevant": [("Cliffball", "Rules"), ("Ridgetoss", "Rules")],
        "expected_answer": "Cliffball scores by landing discs into height tiers, while Ridgetoss scores by throwing discs at flagged target zones based on accuracy rather than height.",
    },
    {
        "question": "Which sport originated from messenger training rather than farming disputes?",
        "relevant": [("Ridgetoss", "Origins")],
        "expected_answer": "Ridgetoss is believed to have started as a training exercise for hillside messengers, unlike Cliffball which came from irrigation disputes.",
    },
]