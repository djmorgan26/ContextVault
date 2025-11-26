#!/usr/bin/env python3
"""
Assign stories to sprints for ContextVault KAN project.

This script maps existing Jira stories to their respective sprints based on sprint_plan.md.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.jira_utils.client import JiraClient
from scripts.jira_utils.parser import parse_sprint_plan


def main():
    print("\n" + "="*70)
    print("Assign Stories to Sprints for KAN")
    print("="*70)

    # Initialize client
    client = JiraClient()

    # Get board ID
    board_id = 2  # KAN Scrum Board

    # Get existing sprints
    print("\n📋 Getting existing sprints...")
    all_sprints = client.jira.sprints(board_id)

    # Map sprint names to IDs (S1-S9)
    sprint_map = {}
    for sprint in all_sprints:
        # Only match S1-S9 pattern (single digit after S)
        if sprint.name.startswith('S') and len(sprint.name) > 1 and sprint.name[1].isdigit():
            try:
                sprint_num = int(sprint.name[1:].split(':')[0])
                sprint_map[sprint_num] = sprint
                print(f"  • Sprint {sprint_num}: {sprint.name} (ID: {sprint.id})")
            except ValueError:
                continue  # Skip invalid sprint names

    # Parse sprint plan
    print("\n📖 Parsing sprint plan...")
    sprints = parse_sprint_plan('docs/archive/sprint_plan.md')
    print(f"✓ Found {len(sprints)} sprints with story assignments")

    # Assign stories to sprints
    print(f"\n📝 Assigning stories to sprints...")

    for sprint_num in range(1, 10):  # Sprint 1-9
        if sprint_num not in sprint_map:
            print(f"  ⚠️  Sprint {sprint_num} not found in Jira")
            continue

        sprint = sprint_map[sprint_num]
        sprint_info = sprints[sprint_num]

        # Build issue keys from story IDs
        story_keys = []
        for story_id in sprint_info.story_ids:
            # Search for story with this ID in summary
            jql = f'project = KAN AND issuetype = Story AND summary ~ "{story_id}:"'
            try:
                issues = client.query_issues(jql, max_results=1)
                if issues:
                    story_keys.append(issues[0].key)
                else:
                    print(f"  ⚠️  Story {story_id} not found in Jira")
            except Exception as e:
                print(f"  ⚠️  Could not find story {story_id}: {e}")

        if story_keys:
            try:
                client.add_issues_to_sprint(sprint.id, story_keys)
                print(f"  ✓ Sprint {sprint_num}: Added {len(story_keys)}/{len(sprint_info.story_ids)} stories")
            except Exception as e:
                print(f"  ✗ Sprint {sprint_num}: Failed to add stories: {e}")
        else:
            print(f"  ⚠️  Sprint {sprint_num}: No stories found to add")

    # Print summary
    print("\n" + "="*70)
    print("✅ Story Assignment Complete!")
    print("="*70)
    print(f"\n🔗 View your board:")
    print(f"   {client.server}/jira/software/c/projects/KAN/board")
    print()


if __name__ == '__main__':
    main()
