import pytest

from scripts.readability import ReadabilityError, validate_readability


def base_report(text: str):
    return {
        "edition_type": "weekly_dossier",
        "developments": [{
            "title": "Short title",
            "what": text,
            "new": "The workflow now stops harmful tests earlier.",
            "not_new": "Teams already use A/B tests and guardrail metrics.",
            "why": "PMs must decide who can stop a test and when.",
            "apply": ["Write the stopping rule before launch."],
            "usefulness": "This sharpens experiment ownership and intervention rules.",
            "decision_trigger": {
                "act_when": "A live test can cause material harm before its planned readout.",
                "monitor_when": "The platform does not support the required guardrail.",
                "ignore_when": "The test is offline and easy to reverse."
            },
            "caveat": "The evidence comes from the vendor."
        }],
        "technique": {
            "title": "Kill-switch table",
            "problem": "Teams often watch tests without agreeing who can stop them.",
            "steps": [{"title": "Set the rule", "body": "Choose the harm threshold before launch."}],
            "example": "A payment test stops when duplicate charges appear.",
            "use_when": "Use it when harm can accumulate quickly.",
            "avoid_when": "Skip it for offline tests.",
            "failure_modes": "Do not choose the threshold after results appear."
        },
        "book": None,
        "foundation": {
            "title": "Guardrails",
            "original": "A guardrail limits harm while the main metric measures value.",
            "holds": "The distinction still prevents teams from optimizing the wrong outcome.",
            "misapplied": "Teams sometimes treat every secondary metric as a veto.",
            "update": "Give each guardrail a threshold and an owner.",
            "question": "Which harm is serious enough to stop this test?"
        },
        "patterns": [{"title": "Control needs an owner", "body": "An alert is useless when nobody can act on it."}],
        "questions": ["Who can stop the test?"]
    }


def test_readability_accepts_short_direct_sentences():
    validate_readability(base_report("Roblox added early warnings for harmful experiments. Teams can stop exposure before the planned readout."))


def test_readability_rejects_sentence_over_thirty_two_words():
    long_sentence = " ".join(["word"] * 33) + "."
    with pytest.raises(ReadabilityError, match="33 words"):
        validate_readability(base_report(long_sentence))


def test_readability_rejects_dense_ai_writing_phrase():
    report = base_report("This marks a pivotal shift in the evolving product landscape.")
    with pytest.raises(ReadabilityError, match="AI-style phrase"):
        validate_readability(report)


def test_readability_rejects_paragraph_over_three_sentences():
    report = base_report("One. Two. Three. Four.")
    with pytest.raises(ReadabilityError, match="more than 3 sentences"):
        validate_readability(report)
