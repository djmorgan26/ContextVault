"""Mapper to convert parsed data models to Jira API field dictionaries."""

from typing import Dict, Any
from .models import Epic, Story


# Priority mapping from doc priority to Jira priority names
PRIORITY_MAP = {
    'P0': 'Highest',
    'P1': 'High',
    'P2': 'Medium',
    'P3': 'Low'
}


def hours_to_story_points(hours: float) -> int:
    """
    Convert hour estimates to Fibonacci story points.

    Args:
        hours: Estimated hours

    Returns:
        Fibonacci story points (1, 2, 3, 5, 8, 13)
    """
    if hours <= 1:
        return 1
    elif hours <= 2:
        return 2
    elif hours <= 4:
        return 3
    elif hours <= 6:
        return 5
    elif hours <= 10:
        return 8
    else:
        return 13


def map_epic_to_jira(epic: Epic, custom_fields: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert Epic object to Jira API fields dictionary.

    Args:
        epic: Epic data model
        custom_fields: Mapping of field names to custom field IDs

    Returns:
        Dictionary ready for Jira issue creation
    """
    description = f"**Goal:** {epic.goal}\n\n**Timeline:** {epic.timeline}"

    # Extract epic number for labels (e.g., "Epic 1" -> "epic-1")
    epic_num = epic.doc_id.lower().replace(' ', '-')

    fields = {
        'project': {'key': 'KAN'},
        'summary': epic.name,
        'description': description,
        'issuetype': {'name': 'Epic'},
        'priority': {'name': PRIORITY_MAP.get(epic.priority, 'Medium')},
        'labels': [epic_num, epic.priority.lower() + '-critical' if epic.priority == 'P0' else epic.priority.lower()]
    }

    # Add Epic Name custom field (standard in Jira)
    if 'Epic Name' in custom_fields:
        fields[custom_fields['Epic Name']] = epic.name

    return fields


def map_story_to_jira(story: Story, epic_key: str, custom_fields: Dict[str, str]) -> Dict[str, Any]:
    """
    Convert Story object to Jira API fields dictionary.

    Args:
        story: Story data model
        epic_key: Jira key of parent epic (e.g., "CV-1")
        custom_fields: Mapping of field names to custom field IDs

    Returns:
        Dictionary ready for Jira issue creation
    """
    # Build description with user story, feature, acceptance criteria, reference docs
    description_parts = [
        f"**User Story:** {story.description}",
        f"",
        f"**Feature:** {story.feature_name}",
        f"",
    ]

    if story.acceptance_criteria:
        description_parts.append("**Acceptance Criteria:**")
        for criterion in story.acceptance_criteria:
            description_parts.append(f"- {criterion}")
        description_parts.append("")

    if story.reference_docs:
        description_parts.append("**Reference Docs:**")
        for doc in story.reference_docs:
            description_parts.append(f"- {doc}")

    description = "\n".join(description_parts)

    # Generate labels from feature and priority
    # e.g., "1.1" -> "feature-1.1-tooling"
    feature_id = story.doc_id.rsplit('.', 1)[0]  # "1.1.1" -> "1.1"
    feature_label = f"feature-{feature_id}"

    # Add type labels based on epic
    type_labels = []
    if 'backend' in story.feature_name.lower() or 'database' in story.feature_name.lower():
        type_labels.append('backend')
    if 'frontend' in story.feature_name.lower() or 'ui' in story.feature_name.lower():
        type_labels.append('frontend')
    if 'test' in story.feature_name.lower():
        type_labels.append('testing')

    labels = [feature_label, story.priority.lower()] + type_labels

    fields = {
        'project': {'key': 'KAN'},
        'summary': f"{story.doc_id}: {story.summary}",
        'description': description,
        'issuetype': {'name': 'Story'},
        'priority': {'name': PRIORITY_MAP.get(story.priority, 'Medium')},
        'labels': labels,
    }

    # Add Epic Link
    if 'Epic Link' in custom_fields:
        fields[custom_fields['Epic Link']] = epic_key

    # Add time tracking (original estimate)
    if story.estimate_hours > 0:
        # Jira expects format like "2h", "30m", "1d"
        if story.estimate_hours < 1:
            minutes = int(story.estimate_hours * 60)
            fields['timetracking'] = {'originalEstimate': f'{minutes}m'}
        else:
            hours = story.estimate_hours
            if hours % 1 == 0:  # Whole hours
                fields['timetracking'] = {'originalEstimate': f'{int(hours)}h'}
            else:  # Fractional hours
                fields['timetracking'] = {'originalEstimate': f'{hours}h'}

    # Add Story Points
    if 'Story Points' in custom_fields and story.estimate_hours > 0:
        fields[custom_fields['Story Points']] = hours_to_story_points(story.estimate_hours)

    return fields


def get_standard_custom_fields() -> Dict[str, str]:
    """
    Get standard custom field IDs that are common across Jira instances.

    These are the default field IDs for Jira Cloud with Scrum template.
    The actual IDs will be verified/updated by querying the Jira API.

    Returns:
        Dictionary mapping field names to custom field IDs
    """
    return {
        'Epic Name': 'customfield_10011',
        'Epic Link': 'customfield_10014',
        'Story Points': 'customfield_10016',
        'Sprint': 'customfield_10020',
    }
