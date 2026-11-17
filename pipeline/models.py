"""Strict structural contracts. These do not validate football interpretations."""
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

Prose = Annotated[str, Field(min_length=40, max_length=6000)]
ShortText = Annotated[str, Field(min_length=4, max_length=300)]


class Strict(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ChartNote(Strict):
    figure_id: str
    explanation: Annotated[str, Field(min_length=40, max_length=2500)]


class Verdict(Strict):
    verdict: Prose


class Style(Strict):
    how_they_play: Prose


class ShapeNotes(Strict):
    last5: Prose
    home: Prose
    away: Prose


class Shape(Strict):
    shape_notes: ShapeNotes
    visualization_analysis: list[ChartNote]


class SpaceNotes(Strict):
    season: Prose
    last5: Prose


class Space(Strict):
    space_notes: SpaceNotes
    visualization_analysis: list[ChartNote]


class Player(Strict):
    player_id: int
    strengths: Prose
    weaknesses: Prose
    how_to_play: Prose


class OtherThreat(Strict):
    player_id: int
    name: str
    number: str
    what_he_does: Prose
    your_response: Prose


class Players(Strict):
    key_players_summary: Prose
    key_players: list[Player]
    other_threats: list[OtherThreat]
    visualization_analysis: list[ChartNote]


class Drill(Strict):
    title: ShortText
    instructions: Prose


class AwarenessItem(Strict):
    title: ShortText
    analysis: Prose
    evidence_refs: Annotated[list[str], Field(min_length=1)]
    drill: Drill | None = None


class Awareness(Strict):
    awareness_summary: Prose
    awareness: Annotated[list[AwarenessItem], Field(min_length=3, max_length=5)]


class AboutData(Strict):
    cutoff: str
    source: str
    fixture_id: int | None
    disclosures: list[str]
    model: str | None
    review_status: str


class About(Strict):
    about: AboutData


SCHEMAS = {
    "verdict": Verdict, "style": Style, "shape": Shape, "space": Space,
    "players": Players, "awareness": Awareness, "about": About,
}


def schema_for(section):
    try:
        return SCHEMAS[section]
    except KeyError as exc:
        raise ValueError(f"Unknown section: {section}") from exc
