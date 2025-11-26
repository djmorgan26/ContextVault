#!/usr/bin/env python3
"""
Create Scrum board and sprints for ContextVault KAN project.

This script:
1. Creates a Scrum board for the KAN project (if needed)
2. Creates 9 sprints based on sprint_plan.md
3. Assigns stories to sprints
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.jira_utils.client import JiraClient
from scripts.jira_utils.parser import parse_sprint_plan


def main():
    print("\n" + "="*70)
    print("Create Scrum Board & Sprints for KAN")
    print("="*70)

    # Initialize client
    client = JiraClient()

    # Check for existing boards
    print("\n📋 Checking existing boards...")
    boards = client.jira.boards()

    scrum_board = None
    for board in boards:
        print(f"  • {board.name} (ID: {board.id}, Type: {board.type})")
        if board.type == 'scrum':
            scrum_board = board
            print(f"    ✓ Found Scrum board!")

    # Create Scrum board if needed
    if not scrum_board:
        print("\n⚠️  No Scrum board found. Creating one...")
        print("Note: Board creation via API may require admin permissions.")
        print()

        # Try to create via API (may fail without admin perms)
        try:
            # Use the REST API directly since jira-python might not have a create_board method
            board_data = {
                "name": "KAN Scrum Board",
                "type": "scrum",
                "filterId": None,  # Will use project filter
                "location": {
                    "type": "project",
                    "projectKeyOrId": "KAN"
                }
            }

            # This might not work - Jira API can be restrictive
            response = client.jira._session.post(
                f"{client.server}/rest/agile/1.0/board",
                json=board_data
            )

            if response.status_code == 201:
                board_info = response.json()
                scrum_board_id = board_info['id']
                print(f"✓ Created Scrum board: {board_info['name']} (ID: {scrum_board_id})")
            else:
                raise Exception(f"API returned {response.status_code}: {response.text}")

        except Exception as e:
            print(f"✗ Could not create Scrum board via API: {e}")
            print()
            print("Please create a Scrum board manually:")
            print("1. Go to: https://davidjmorgan26.atlassian.net/jira/software/c/projects/KAN")
            print("2. Click 'Board' dropdown → 'Create board'")
            print("3. Choose 'Scrum board'")
            print("4. Name it 'KAN Scrum Board'")
            print("5. Re-run this script")
            sys.exit(1)
    else:
        scrum_board_id = scrum_board.id
        print(f"\n✓ Using Scrum board: {scrum_board.name} (ID: {scrum_board_id})")

    # Parse sprint plan
    print("\n📖 Parsing sprint plan...")
    sprints = parse_sprint_plan('docs/archive/sprint_plan.md')
    print(f"✓ Found {len(sprints)} sprints to create")

    # Create sprints
    print(f"\n🏃 Creating sprints...")
    created_sprints = {}

    for sprint_num in sorted(sprints.keys()):
        sprint_info = sprints[sprint_num]

        # Sprint 1 starts today, others are unscheduled
        if sprint_num == 1:
            start_date = datetime.now()
            end_date = start_date + timedelta(weeks=2)
        else:
            start_date = None
            end_date = None

        try:
            sprint = client.create_sprint(
                scrum_board_id,
                f"Sprint {sprint_num}: {sprint_info.name}",
                start_date=start_date,
                end_date=end_date
            )
            created_sprints[sprint_num] = sprint

        except Exception as e:
            print(f"  ✗ Failed to create Sprint {sprint_num}: {e}")
            continue

    print(f"\n✓ Created {len(created_sprints)} sprints")

    # Assign stories to sprints
    print(f"\n📝 Assigning stories to sprints...")

    for sprint_num, sprint in created_sprints.items():
        sprint_info = sprints[sprint_num]

        # Build issue keys from story IDs
        # Story IDs like "1.1.1" need to be mapped to KAN-XX issue keys
        # We need to query Jira to find which KAN-XX corresponds to which story ID

        story_keys = []
        for story_id in sprint_info.story_ids:
            # Search for story with this ID in summary
            jql = f'project = KAN AND issuetype = Story AND summary ~ "{story_id}:"'
            try:
                issues = client.query_issues(jql, max_results=1)
                if issues:
                    story_keys.append(issues[0].key)
            except Exception as e:
                print(f"  ⚠️  Could not find story {story_id}: {e}")

        if story_keys:
            try:
                client.add_issues_to_sprint(sprint.id, story_keys)
                print(f"  ✓ Sprint {sprint_num}: Added {len(story_keys)} stories")
            except Exception as e:
                print(f"  ✗ Sprint {sprint_num}: Failed to add stories: {e}")
        else:
            print(f"  ⚠️  Sprint {sprint_num}: No stories found")

    # Print summary
    print("\n" + "="*70)
    print("✅ Sprint Setup Complete!")
    print("="*70)
    print(f"\nCreated {len(created_sprints)} sprints")
    print(f"\n🔗 View your board:")
    print(f"   {client.server}/jira/software/c/projects/KAN/board")
    print()


if __name__ == '__main__':
    main()
