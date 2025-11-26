#!/usr/bin/env python3
"""
Jira Migration Script for ContextVault

Migrates project documentation from markdown files to Jira.
Creates epics, stories, and sprints based on docs/epics_features_stories.md
and docs/sprint_plan.md.

Usage:
    python scripts/jira_migrate.py --dry-run    # Preview what will be created
    python scripts/jira_migrate.py              # Full migration
    python scripts/jira_migrate.py --epic 1     # Migrate only Epic 1
    python scripts/jira_migrate.py --sprint 1   # Migrate only Sprint 1
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.jira_utils.client import JiraClient
from scripts.jira_utils.parser import parse_epics_file, parse_sprint_plan, get_sprint_for_story
from scripts.jira_utils.mapper import map_epic_to_jira, map_story_to_jira


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='Migrate ContextVault project to Jira')
    parser.add_argument('--dry-run', action='store_true', help='Preview without creating issues')
    parser.add_argument('--epic', type=int, help='Migrate only specific epic number (1-11)')
    parser.add_argument('--sprint', type=int, help='Migrate only specific sprint number (1-9)')
    args = parser.parse_args()

    print("\n" + "="*70)
    print("ContextVault → Jira Migration")
    print("="*70)

    if args.dry_run:
        print("\n🔍 DRY-RUN MODE - No issues will be created\n")

    # Parse markdown documentation
    print("\n📖 Parsing documentation files...")
    epics_file = Path('docs/epics_features_stories.md')
    sprint_file = Path('docs/sprint_plan.md')

    if not epics_file.exists():
        print(f"✗ Error: {epics_file} not found")
        sys.exit(1)

    if not sprint_file.exists():
        print(f"✗ Error: {sprint_file} not found")
        sys.exit(1)

    epics = parse_epics_file(str(epics_file))
    sprints = parse_sprint_plan(str(sprint_file))

    print(f"✓ Parsed {len(epics)} epics with {sum(len(e.stories) for e in epics)} stories")
    print(f"✓ Parsed {len(sprints)} sprints")

    # Filter if specific epic/sprint requested
    if args.epic:
        epics = [e for e in epics if e.doc_id == f"Epic {args.epic}"]
        if not epics:
            print(f"✗ Error: Epic {args.epic} not found")
            sys.exit(1)
        print(f"\n📌 Migrating only Epic {args.epic}")

    if args.sprint:
        if args.sprint not in sprints:
            print(f"✗ Error: Sprint {args.sprint} not found")
            sys.exit(1)
        sprint_story_ids = sprints[args.sprint].story_ids
        # Filter stories to only those in this sprint
        for epic in epics:
            epic.stories = [s for s in epic.stories if s.doc_id in sprint_story_ids]
        print(f"\n📌 Migrating only Sprint {args.sprint}")

    if args.dry_run:
        print_dry_run_summary(epics, sprints)
        return

    # Initialize Jira client
    print("\n🔗 Connecting to Jira...")
    try:
        client = JiraClient()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

    # Verify/create project
    print("\n📁 Verifying project...")
    try:
        project = client.get_or_create_project('KAN', 'ContextVault')
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

    # Create epics
    print(f"\n📋 Creating {len(epics)} epics...")
    epic_keys = {}

    for epic in epics:
        epic_fields = map_epic_to_jira(epic, client.custom_fields)
        try:
            issue = client.create_epic(epic_fields)
            epic_keys[epic.doc_id] = issue.key
        except Exception as e:
            print(f"✗ Failed to create epic '{epic.name}': {e}")
            continue

    if not epic_keys:
        print("\n✗ No epics created. Aborting.")
        sys.exit(1)

    # Create stories
    print(f"\n📝 Creating stories...")
    story_keys = {}
    story_count = 0

    for epic in epics:
        if epic.doc_id not in epic_keys:
            continue

        epic_key = epic_keys[epic.doc_id]
        print(f"\n  Epic {epic_key}: {epic.name}")

        if not epic.stories:
            print(f"    (No stories in this epic)")
            continue

        for story in epic.stories:
            story_fields = map_story_to_jira(story, epic_key, client.custom_fields)
            try:
                issue = client.create_story(story_fields)
                story_keys[story.doc_id] = issue.key
                story_count += 1
            except Exception as e:
                print(f"  ✗ Failed to create story '{story.doc_id}': {e}")
                continue

    print(f"\n✓ Created {story_count} stories")

    # Create sprints and assign stories
    if not args.epic:  # Only create sprints if not filtering by epic
        print(f"\n🏃 Creating {len(sprints)} sprints...")
        try:
            board_id = client.get_board_id('KAN')
        except Exception as e:
            print(f"✗ Error getting board: {e}")
            print("Skipping sprint creation")
            board_id = None

        if board_id:
            sprint_ids = {}
            for sprint_num in sorted(sprints.keys())[:9]:  # Only first 9 sprints
                sprint_info = sprints[sprint_num]

                # Sprint 1 starts today, others have no start date
                start_date = datetime.now() if sprint_num == 1 else None

                try:
                    sprint = client.create_sprint(
                        board_id,
                        f"Sprint {sprint_num}: {sprint_info.name}",
                        start_date=start_date
                    )
                    sprint_ids[sprint_num] = sprint.id

                    # Assign stories to sprint
                    sprint_story_keys = [
                        story_keys[story_id]
                        for story_id in sprint_info.story_ids
                        if story_id in story_keys
                    ]

                    if sprint_story_keys:
                        client.add_issues_to_sprint(sprint.id, sprint_story_keys)

                except Exception as e:
                    print(f"✗ Failed to create sprint {sprint_num}: {e}")
                    continue

            print(f"\n✓ Created {len(sprint_ids)} sprints")

    # GitHub integration instructions
    client.configure_github_integration('https://github.com/djmorgan26/ContextVault')

    # Print summary
    print("\n" + "="*70)
    print("✅ Migration Complete!")
    print("="*70)
    print(f"\nCreated:")
    print(f"  • {len(epic_keys)} epics")
    print(f"  • {story_count} stories")
    if not args.epic:
        print(f"  • {len(sprints)} sprints")

    print(f"\n🔗 View your Jira board:")
    print(f"   {client.server}/jira/software/c/projects/KAN")

    print(f"\n📚 Next steps:")
    print(f"  1. Review the Jira board to ensure everything looks correct")
    print(f"  2. Configure GitHub integration (see instructions above)")
    print(f"  3. Start Sprint 1 (already scheduled to start today)")
    print(f"  4. Archive markdown docs: mkdir -p docs/archive && mv docs/epics_features_stories.md docs/sprint_plan.md docs/archive/")
    print(f"  5. Commit changes: git add -A && git commit -m 'Migrate project to Jira'")
    print()


def print_dry_run_summary(epics, sprints):
    """Print summary of what would be created."""
    print("\n" + "="*70)
    print("DRY-RUN SUMMARY")
    print("="*70)

    total_stories = sum(len(e.stories) for e in epics)

    print(f"\nWould create:")
    print(f"  • {len(epics)} epics")
    print(f"  • {total_stories} stories")
    print(f"  • {len(sprints)} sprints")

    print(f"\nEpics:")
    for epic in epics:
        print(f"  • {epic.doc_id}: {epic.name} ({epic.priority}) - {len(epic.stories)} stories")

    print(f"\nSprints:")
    for sprint_num, sprint_info in sorted(sprints.items()):
        start_indicator = " [STARTS TODAY]" if sprint_num == 1 else ""
        print(f"  • Sprint {sprint_num}: {sprint_info.name} - {len(sprint_info.story_ids)} stories{start_indicator}")

    print(f"\nTo proceed with migration, run without --dry-run flag")
    print()


if __name__ == '__main__':
    main()
