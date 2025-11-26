#!/usr/bin/env python3
"""
Jira Export Utility for ContextVault

Export Jira project data to markdown format for backup/reporting.

Usage:
    python scripts/jira_export.py --output docs/jira_backup.md
    python scripts/jira_export.py --sprint current --output sprint_report.md
"""

import argparse
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.jira_utils.client import JiraClient


def export_all(client: JiraClient, output_file: str):
    """Export all project data to markdown."""
    print(f"\n📤 Exporting all project data to {output_file}...")

    try:
        # Query all issues
        jql = 'project = KAN ORDER BY created ASC'
        issues = client.query_issues(jql, max_results=1000)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# ContextVault - Jira Export\n\n")
            f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Issues:** {len(issues)}\n\n")
            f.write("---\n\n")

            # Group by epic
            epics = [i for i in issues if i.fields.issuetype.name == 'Epic']
            stories = [i for i in issues if i.fields.issuetype.name == 'Story']

            f.write(f"## Epics ({len(epics)})\n\n")

            for epic in epics:
                f.write(f"### {epic.key}: {epic.fields.summary}\n\n")
                f.write(f"**Priority:** {epic.fields.priority.name}\n\n")
                f.write(f"**Status:** {epic.fields.status.name}\n\n")

                # Find stories in this epic
                epic_stories = [
                    s for s in stories
                    if hasattr(s.fields, 'customfield_10014')
                    and s.fields.customfield_10014 == epic.key
                ]

                if epic_stories:
                    f.write(f"**Stories ({len(epic_stories)}):**\n\n")
                    for story in epic_stories:
                        status = story.fields.status.name
                        f.write(f"- [{status}] {story.key}: {story.fields.summary}\n")

                f.write("\n")

        print(f"✓ Exported {len(issues)} issues to {output_file}")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def export_sprint(client: JiraClient, sprint_id: str, output_file: str):
    """Export sprint data to markdown."""
    print(f"\n📤 Exporting sprint {sprint_id} to {output_file}...")

    try:
        if sprint_id == 'current':
            board_id = client.get_board_id('KAN')
            sprint = client.get_current_sprint(board_id)
            if not sprint:
                print("No active sprint")
                return
            sprint_id = sprint.id
            sprint_name = sprint.name
        else:
            sprint_name = f"Sprint {sprint_id}"

        # Query sprint issues
        jql = f'sprint = {sprint_id} ORDER BY priority DESC, created ASC'
        issues = client.query_issues(jql, max_results=100)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {sprint_name} - Report\n\n")
            f.write(f"**Exported:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Issues:** {len(issues)}\n\n")
            f.write("---\n\n")

            # Group by status
            statuses = {}
            for issue in issues:
                status = issue.fields.status.name
                if status not in statuses:
                    statuses[status] = []
                statuses[status].append(issue)

            for status, status_issues in statuses.items():
                f.write(f"## {status} ({len(status_issues)})\n\n")
                for issue in status_issues:
                    priority = issue.fields.priority.name
                    f.write(f"- [{priority}] {issue.key}: {issue.fields.summary}\n")
                f.write("\n")

        print(f"✓ Exported {len(issues)} issues to {output_file}")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)


def main():
    """Main export function."""
    parser = argparse.ArgumentParser(description='Export Jira data to markdown')
    parser.add_argument('--output', type=str, required=True, help='Output markdown file')
    parser.add_argument('--sprint', type=str, help='Sprint ID or "current"')
    args = parser.parse_args()

    try:
        client = JiraClient()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

    if args.sprint:
        export_sprint(client, args.sprint, args.output)
    else:
        export_all(client, args.output)

    print()


if __name__ == '__main__':
    main()
