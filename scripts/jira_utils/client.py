"""Jira API client wrapper."""

import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from jira import JIRA
from jira.exceptions import JIRAError
from dotenv import load_dotenv


class JiraClient:
    """Wrapper around jira-python library for ContextVault migration."""

    def __init__(self):
        """Initialize Jira client with credentials from environment."""
        load_dotenv()

        self.server = os.getenv('JIRA_BASE_URL')
        self.email = os.getenv('JIRA_EMAIL')
        self.api_token = os.getenv('JIRA_API_TOKEN')
        self.space = os.getenv('JIRA_SPACE', 'ContextVault')

        if not all([self.server, self.email, self.api_token]):
            raise ValueError(
                "Missing Jira credentials. Please set JIRA_BASE_URL, JIRA_EMAIL, "
                "and JIRA_API_TOKEN in .env file"
            )

        # Remove trailing slash from server URL if present
        self.server = self.server.rstrip('/')

        print(f"Connecting to Jira at {self.server}...")
        self.jira = JIRA(
            server=self.server,
            basic_auth=(self.email, self.api_token)
        )
        print("✓ Connected to Jira successfully")

        self.custom_fields = self._get_custom_field_mapping()

    def _get_custom_field_mapping(self) -> Dict[str, str]:
        """
        Query Jira to get actual custom field IDs.

        Returns:
            Dictionary mapping field names to custom field IDs
        """
        print("Fetching custom field IDs...")
        fields = self.jira.fields()

        field_map = {}
        for field in fields:
            if field['name'] == 'Epic Name':
                field_map['Epic Name'] = field['id']
            elif field['name'] == 'Epic Link':
                field_map['Epic Link'] = field['id']
            elif field['name'] == 'Story Points' or field['name'] == 'Story point estimate':
                field_map['Story Points'] = field['id']
            elif field['name'] == 'Sprint':
                field_map['Sprint'] = field['id']

        print(f"✓ Found custom fields: {field_map}")
        return field_map

    def get_or_create_project(self, key: str, name: str) -> Any:
        """
        Check if project exists, create if not.

        Args:
            key: Project key (e.g., "CV")
            name: Project name (e.g., "ContextVault")

        Returns:
            Jira Project object
        """
        try:
            project = self.jira.project(key)
            print(f"✓ Project '{key}' already exists")
            return project
        except JIRAError as e:
            if e.status_code == 404:
                raise RuntimeError(
                    f"Project '{key}' not found in Jira.\n"
                    f"Available projects: {[p.key for p in self.jira.projects()]}\n"
                    f"Please check the project key or create it manually."
                )
            else:
                raise

    def create_epic(self, epic_fields: Dict[str, Any]) -> Any:
        """
        Create an epic in Jira.

        Args:
            epic_fields: Dictionary of epic fields (from mapper)

        Returns:
            Created Jira Issue object
        """
        try:
            issue = self.jira.create_issue(fields=epic_fields)
            print(f"✓ Created epic: {issue.key} - {epic_fields['summary']}")
            time.sleep(0.5)  # Rate limiting
            return issue
        except JIRAError as e:
            print(f"✗ Failed to create epic: {e.text}")
            raise

    def create_story(self, story_fields: Dict[str, Any]) -> Any:
        """
        Create a story in Jira.

        Args:
            story_fields: Dictionary of story fields (from mapper)

        Returns:
            Created Jira Issue object
        """
        try:
            issue = self.jira.create_issue(fields=story_fields)
            print(f"  ✓ Created story: {issue.key} - {story_fields['summary'][:60]}...")
            time.sleep(0.3)  # Rate limiting
            return issue
        except JIRAError as e:
            print(f"  ✗ Failed to create story: {e.text}")
            print(f"     Fields: {story_fields}")
            raise

    def get_board_id(self, project_key: str) -> int:
        """
        Get the board ID for a project.

        Args:
            project_key: Project key (e.g., "CV")

        Returns:
            Board ID
        """
        boards = self.jira.boards()
        for board in boards:
            if hasattr(board, 'location') and board.location.project_key == project_key:
                print(f"✓ Found board: {board.name} (ID: {board.id})")
                return board.id

        # If no board found, take first board or raise error
        if len(boards) > 0:
            board = boards[0]
            print(f"⚠ Using board: {board.name} (ID: {board.id})")
            return board.id

        raise RuntimeError(f"No board found for project {project_key}")

    def create_sprint(
        self,
        board_id: int,
        name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Any:
        """
        Create a sprint on the board.

        Args:
            board_id: Board ID
            name: Sprint name
            start_date: Sprint start date (optional)
            end_date: Sprint end date (optional, defaults to 2 weeks after start)

        Returns:
            Created Sprint object
        """
        try:
            # If start_date provided, calculate end_date if not provided
            if start_date and not end_date:
                end_date = start_date + timedelta(weeks=2)

            sprint = self.jira.create_sprint(
                name=name,
                board_id=board_id,
                startDate=start_date.isoformat() if start_date else None,
                endDate=end_date.isoformat() if end_date else None
            )
            print(f"✓ Created sprint: {name} (ID: {sprint.id})")
            time.sleep(0.3)
            return sprint
        except JIRAError as e:
            print(f"✗ Failed to create sprint: {e.text}")
            raise

    def add_issues_to_sprint(self, sprint_id: int, issue_keys: List[str]):
        """
        Add multiple issues to a sprint.

        Args:
            sprint_id: Sprint ID
            issue_keys: List of issue keys (e.g., ["CV-1", "CV-2"])
        """
        try:
            self.jira.add_issues_to_sprint(sprint_id, issue_keys)
            print(f"  ✓ Added {len(issue_keys)} issues to sprint {sprint_id}")
            time.sleep(0.3)
        except JIRAError as e:
            print(f"  ✗ Failed to add issues to sprint: {e.text}")
            raise

    def query_issues(self, jql: str, max_results: int = 100) -> List[Any]:
        """
        Query Jira issues using JQL.

        Args:
            jql: JQL query string
            max_results: Maximum number of results

        Returns:
            List of Jira Issue objects
        """
        try:
            issues = self.jira.search_issues(jql, maxResults=max_results)
            return issues
        except JIRAError as e:
            print(f"✗ Failed to query issues: {e.text}")
            raise

    def get_current_sprint(self, board_id: int) -> Optional[Any]:
        """
        Get the currently active sprint for a board.

        Args:
            board_id: Board ID

        Returns:
            Active Sprint object or None
        """
        try:
            sprints = self.jira.sprints(board_id, state='active')
            if sprints:
                return sprints[0]
            return None
        except JIRAError as e:
            print(f"✗ Failed to get current sprint: {e.text}")
            return None

    def configure_github_integration(self, repo_url: str):
        """
        Configure GitHub integration for the project.

        Note: This typically requires installing the GitHub for Jira app
        from the Atlassian Marketplace. This method provides instructions.

        Args:
            repo_url: GitHub repository URL
        """
        print("\n" + "="*70)
        print("GitHub Integration Setup")
        print("="*70)
        print(f"\nTo enable automatic commit linking with Jira:")
        print(f"\n1. Install 'GitHub for Jira' app:")
        print(f"   {self.server}/plugins/servlet/ac/com.github.integration.production/github-post-install-page")
        print(f"\n2. Connect your GitHub repository:")
        print(f"   - Repository: {repo_url}")
        print(f"   - This will enable:")
        print(f"     • Commits with 'CV-XX' automatically link to issues")
        print(f"     • Smart commits (CV-XX #comment, #done, etc.)")
        print(f"     • PR/branch visibility in Jira issues")
        print(f"\n3. Test with a commit:")
        print(f"   git commit -m 'CV-1: Test commit linking'")
        print("\n" + "="*70 + "\n")
