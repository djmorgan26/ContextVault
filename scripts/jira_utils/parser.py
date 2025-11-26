"""Parser for extracting epics and stories from markdown documentation."""

import re
from typing import List, Dict, Tuple, Optional
from .models import Epic, Story, Feature, SprintInfo


def parse_epics_file(filepath: str) -> List[Epic]:
    """
    Parse epics_features_stories.md file.

    Extracts all epics, features, and user stories with their metadata.

    Returns:
        List of Epic objects with nested stories
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    epics = []
    epic_pattern = r'^## (Epic \d+): (.+?) \[(P\d)\]$'

    # Split content by epic headers
    epic_sections = re.split(r'^(?=## Epic)', content, flags=re.MULTILINE)
    epic_sections = [s for s in epic_sections if s.strip() and '## Epic' in s]

    for section in epic_sections:
        lines = section.split('\n')

        # Parse epic header
        header_match = re.match(epic_pattern, lines[0])
        if not header_match:
            continue

        epic_id = header_match.group(1)
        epic_name = header_match.group(2)
        epic_priority = header_match.group(3)

        # Extract goal and timeline
        goal = ""
        timeline = ""
        for line in lines[1:10]:  # Check first few lines
            if line.startswith('**Goal:**'):
                goal = line.replace('**Goal:**', '').strip()
            elif line.startswith('**Timeline:**'):
                timeline = line.replace('**Timeline:**', '').strip()

        epic = Epic(
            doc_id=epic_id,
            name=epic_name,
            goal=goal,
            timeline=timeline,
            priority=epic_priority
        )

        # Parse features and stories within this epic
        current_feature = None
        current_story = None
        in_acceptance_criteria = False
        acceptance_criteria = []

        for i, line in enumerate(lines):
            # Feature header
            if line.startswith('### Feature'):
                # Save previous feature if exists
                if current_feature:
                    epic.features.append(current_feature)

                # Parse feature: "### Feature 1.1: Project Structure & Tooling"
                feature_match = re.match(r'^### Feature ([\d.]+): (.+)$', line)
                if feature_match:
                    feature_id = feature_match.group(1)
                    feature_name = feature_match.group(2)
                    current_feature = Feature(feature_id=feature_id, name=feature_name)

            # User Story header
            elif line.startswith('**User Story'):
                # Save previous story if exists
                if current_story and current_feature:
                    current_story.acceptance_criteria = acceptance_criteria.copy()
                    current_feature.stories.append(current_story)
                    epic.stories.append(current_story)
                    acceptance_criteria = []

                # Parse: "**User Story 1.1.1:** As a developer..."
                story_match = re.match(r'^\*\*User Story ([\d.]+):\*\* (.+)$', line)
                if story_match:
                    story_id = story_match.group(1)
                    story_summary = story_match.group(2)

                    current_story = Story(
                        doc_id=story_id,
                        summary=story_summary,
                        description=story_summary,
                        feature_name=current_feature.name if current_feature else "",
                        acceptance_criteria=[],
                        estimate_hours=0.0,
                        priority=epic_priority,  # Default to epic priority
                        status="Not Started",
                        reference_docs=[],
                        epic_id=epic_id
                    )
                    in_acceptance_criteria = False

            # Acceptance Criteria section
            elif '**Acceptance Criteria:**' in line:
                in_acceptance_criteria = True

            # Acceptance criteria items
            elif in_acceptance_criteria and line.strip().startswith('-') and '**' not in line:
                criterion = line.strip().lstrip('- ').strip()
                if criterion:
                    acceptance_criteria.append(criterion)

            # End of acceptance criteria
            elif in_acceptance_criteria and line.strip().startswith('- **') and 'Acceptance' not in line:
                in_acceptance_criteria = False

            # Metadata fields
            elif current_story:
                if line.startswith('- **Priority:**'):
                    priority_match = re.search(r'(P\d)', line)
                    if priority_match:
                        current_story.priority = priority_match.group(1)

                elif line.startswith('- **Estimate:**'):
                    estimate_match = re.search(r'(\d+(?:\.\d+)?)\s*(hours?|h)', line, re.IGNORECASE)
                    if estimate_match:
                        current_story.estimate_hours = float(estimate_match.group(1))
                    # Handle minute estimates
                    minute_match = re.search(r'(\d+)\s*min', line, re.IGNORECASE)
                    if minute_match:
                        current_story.estimate_hours = float(minute_match.group(1)) / 60.0

                elif line.startswith('- **Status:**'):
                    status = line.replace('- **Status:**', '').strip()
                    current_story.status = status

                elif line.startswith('- **Reference Docs:**'):
                    # Start collecting reference docs
                    pass
                elif line.strip().startswith('- `') and 'docs/' in line:
                    # Reference doc line
                    doc = line.strip().lstrip('- ').strip('`')
                    current_story.reference_docs.append(doc)

        # Save last story and feature
        if current_story and current_feature:
            current_story.acceptance_criteria = acceptance_criteria.copy()
            current_feature.stories.append(current_story)
            epic.stories.append(current_story)

        if current_feature:
            epic.features.append(current_feature)

        epics.append(epic)

    return epics


def parse_sprint_plan(filepath: str) -> Dict[int, SprintInfo]:
    """
    Parse sprint_plan.md file.

    Extracts sprint information and story assignments.

    Returns:
        Dictionary mapping sprint number to SprintInfo
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    sprints = {}

    # Pattern: ## Sprint 1: Foundation & Security Core (Week 1-2)
    sprint_pattern = r'^## Sprint (\d+): (.+?) \((.+?)\)$'

    # Split by sprint headers
    sprint_sections = re.split(r'^(?=## Sprint)', content, flags=re.MULTILINE)
    sprint_sections = [s for s in sprint_sections if s.strip() and '## Sprint' in s]

    for section in sprint_sections:
        lines = section.split('\n')

        # Parse sprint header
        header_match = re.match(sprint_pattern, lines[0])
        if not header_match:
            continue

        sprint_num = int(header_match.group(1))
        sprint_name = header_match.group(2)
        weeks = header_match.group(3)

        # Extract goal/focus
        focus = ""
        for line in lines[1:5]:
            if line.startswith('**Goal:**'):
                focus = line.replace('**Goal:**', '').strip()
                break

        # Extract story assignments
        story_ids = []
        total_estimate = 0.0
        in_stories_section = False

        for line in lines:
            # Check for story checkboxes: - [ ] **1.1.1** Backend directory structure (2h)
            story_match = re.match(r'^- \[ \] \*\*([\d.]+)\*\*', line)
            if story_match:
                story_id = story_match.group(1)
                story_ids.append(story_id)

                # Extract estimate
                estimate_match = re.search(r'\((\d+(?:\.\d+)?)\s*h\)', line)
                if estimate_match:
                    total_estimate += float(estimate_match.group(1))

        # Look for total estimate
        estimate_match = re.search(r'\*\*Total Estimate:\*\* ([\d.]+) hours?', '\n'.join(lines))
        if estimate_match:
            total_estimate = float(estimate_match.group(1))

        sprint_info = SprintInfo(
            sprint_num=sprint_num,
            name=sprint_name,
            focus=focus,
            story_ids=story_ids,
            estimate_hours=total_estimate,
            weeks=weeks
        )

        sprints[sprint_num] = sprint_info

    return sprints


def get_sprint_for_story(story_id: str, sprints: Dict[int, SprintInfo]) -> Optional[int]:
    """
    Find which sprint a story is assigned to.

    Args:
        story_id: Story doc ID (e.g., "1.1.1")
        sprints: Dictionary of sprint information

    Returns:
        Sprint number or None if not assigned
    """
    for sprint_num, sprint_info in sprints.items():
        if story_id in sprint_info.story_ids:
            return sprint_num
    return None
