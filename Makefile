.PHONY: help jira-migrate-dry jira-migrate jira-export jira-sprint jira-backlog

help:
	@echo "ContextVault - Makefile"
	@echo ""
	@echo "Jira Management:"
	@echo "  make jira-migrate-dry  - Preview Jira migration (dry-run)"
	@echo "  make jira-migrate      - Run full Jira migration"
	@echo "  make jira-export       - Export Jira to markdown backup"
	@echo "  make jira-sprint       - Show current sprint"
	@echo "  make jira-backlog      - Show backlog items"

jira-migrate-dry:
	python3 scripts/jira_migrate.py --dry-run

jira-migrate:
	python3 scripts/jira_migrate.py

jira-export:
	@mkdir -p docs/archive
	python3 scripts/jira_export.py --output docs/archive/jira_backup.md

jira-sprint:
	python3 scripts/jira_query.py --current-sprint

jira-backlog:
	python3 scripts/jira_query.py --backlog --limit 20
