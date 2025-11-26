"""Data models for Jira migration."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Story:
    """User story data model."""
    doc_id: str  # e.g., "1.1.1"
    summary: str
    description: str
    feature_name: str
    acceptance_criteria: List[str]
    estimate_hours: float
    priority: str  # P0, P1, P2, P3
    status: str  # Not Started, In Progress, Complete
    reference_docs: List[str]
    epic_id: str  # e.g., "Epic 1"
    sprint_id: Optional[int] = None


@dataclass
class Feature:
    """Feature grouping (for documentation purposes)."""
    feature_id: str  # e.g., "1.1"
    name: str
    stories: List[Story] = field(default_factory=list)


@dataclass
class Epic:
    """Epic data model."""
    doc_id: str  # e.g., "Epic 1"
    name: str
    goal: str
    timeline: str
    priority: str  # P0, P1, P2, P3
    features: List[Feature] = field(default_factory=list)
    stories: List[Story] = field(default_factory=list)


@dataclass
class SprintInfo:
    """Sprint information."""
    sprint_num: int
    name: str
    focus: str
    story_ids: List[str]  # List of story doc_ids
    estimate_hours: float
    weeks: str  # e.g., "Week 1-2"
