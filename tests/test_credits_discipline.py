"""Role-aware credits + editorial discipline tests (pure, deterministic)."""

import json

from cultural_calendar import legacy as L


def test_format_credits_roles_and_order():
    people = json.dumps([
        {"name": "Christopher Nolan", "role": "Director"},
        {"name": "Jane Writer", "role": "Writer"},
        {"name": "Matt Damon", "role": "Cast"},
        {"name": "Tom Holland", "role": "Cast"},
    ])
    out = L.format_credits(people)
    assert "Directed by Christopher Nolan" in out
    assert "Written by Jane Writer" in out
    assert "With Matt Damon, Tom Holland" in out


def test_format_credits_suppresses_artist_and_drops_ep():
    # Album artist role is suppressed (already in the title).
    assert L.format_credits(json.dumps([{"name": "Adele", "role": "Artist"}])) == ""
    # Executive Producer is not a displayable role.
    assert "Exec" not in L.format_credits(json.dumps([{"name": "X", "role": "Executive Producer"}]))


def test_tv_creator_and_showrunner_kept():
    out = L.format_credits(json.dumps([
        {"name": "A Creator", "role": "Creator"},
        {"name": "B Runner", "role": "Showrunner"},
        {"name": "C Lead", "role": "Cast"},
    ]))
    assert "Created by A Creator" in out and "Showrunner B Runner" in out and "With C Lead" in out


def test_carried_over_titles():
    assert L.is_carried_over_title("Wicked")
    assert L.is_carried_over_title("Hamilton")
    assert not L.is_carried_over_title("Some Brand New Play")


def test_dedupe_title_normalization():
    a = L.normalized_dedupe_title("Chess")
    b = L.normalized_dedupe_title("Chess: The Musical")
    assert a == b  # same production collapses across sources
