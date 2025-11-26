#!/usr/bin/env python3
"""
Jira Query Utility for ContextVault

Quick CLI tool to query Jira for current sprint, backlog, and epic stories.

Usage:
    python scripts/jira_query.py --current-sprint
    python scripts/jira_query.py --backlog --limit 20
    python scripts/jira_query.py --epic CV-1
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.jira_utils.client import JiraClient


def query_current_sprint(client: JiraClient):
    """Display current sprint stories."""
    print("\n📅 Current Sprint")
    print("="*70)

    try:
        board_id = client.get_board_id('KAN')
        sprint = client.get_current_sprint(board_id)

        if not sprint:
            print("No active sprint")
            return

        print(f"\n{sprint.name}")
        print(f"State: {sprint.state}")
        if hasattr(sprint, 'startDate'):
            print(f"Start: {sprint.startDate}")
        if hasattr(sprint, 'endDate'):
            print(f"End: {sprint.endDate}")

        # Query issues in sprint
        jql = f'sprint = {sprint.id} ORDER BY priority DESC, created ASC'
        issues = client.query_issues(jql, max_results=100)

        print(f"\nIssues ({len(issues)}):")
        for issue in issues:
            status = issue.fields.status.name
            print(f"  [{status:12}] {issue.key}: {issue.fields.summary[:60]}")

    except Exception as e:
        print(f"✗ Error: {e}")


def query_backlog(client: JiraClient, limit: int = 10):
    """Display backlog stories."""
    print(f"\n📋 Backlog (Top {limit})")
    print("="*70)

    try:
        jql = 'project = KAN AND sprint is EMPTY AND status != Done ORDER BY priority DESC, created ASC'
        issues = client.query_issues(jql, max_results=limit)

        if not issues:
            print("No backlog items")
            return

        print(f"\nItems ({len(issues)}):")
        for issue in issues:
            priority = issue.fields.priority.name
            issue_type = issue.fields.issuetype.name
            print(f"  [{priority:8}] {issue.key} ({issue_type}): {issue.fields.summary[:50]}")

    except Exception as e:
        print(f"✗ Error: {e}")


def query_epic(client: JiraClient, epic_key: str):
    """Display all stories in an epic."""
    print(f"\n📖 Epic {epic_key}")
    print("="*70)

    try:
        # Get epic details
        epic = client.jira.issue(epic_key)
        print(f"\n{epic.fields.summary}")
        print(f"Priority: {epic.fields.priority.name}")
        print(f"Status: {epic.fields.status.name}")

        # Query stories in epic
        # Note: Epic Link field ID might vary, using common one
        jql = f'"Epic Link" = {epic_key} ORDER BY created ASC'
        issues = client.query_issues(jql, max_results=100)

        print(f"\nStories ({len(issues)}):")
        for issue in issues:
            status = issue.fields.status.name
            estimate = getattr(issue.fields, 'timeoriginalestimate', None)
            estimate_str = f"{estimate//3600}h" if estimate else "  -"
            print(f"  [{status:12}] {issue.key} ({estimate_str:4}): {issue.fields.summary[:50]}")

    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Main query function."""
    parser = argparse.ArgumentParser(description='Query Jira for ContextVault project')
    parser.add_argument('--current-sprint', action='store_true', help='Show current sprint')
    parser.add_argument('--backlog', action='store_true', help='Show backlog')
    parser.add_argument('--epic', type=str, help='Show epic stories (e.g., CV-1)')
    parser.add_argument('--limit', type=int, default=10, help='Limit results (default: 10)')
    args = parser.parse_args()

    if not any([args.current_sprint, args.backlog, args.epic]):
        parser.print_help()
        sys.exit(1)

    try:
        client = JiraClient()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

    if args.current_sprint:
        query_current_sprint(client)

    if args.backlog:
        query_backlog(client, args.limit)

    if args.epic:
        query_epic(client, args.epic)

    print()


if __name__ == '__main__':
    main()
