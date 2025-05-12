#!/usr/bin/env python3
"""
Changelog Generator

This script extracts changelog information from PR descriptions based on a template
and updates the appropriate changelog files organized by version.
"""

import logging
import os
import re
import subprocess
import sys
import traceback
from datetime import datetime
from github import Github
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('changelog-generator')


class ChangelogGenerator:
	"""Main class for generating changelogs from PR descriptions."""

	def __init__(self):
		"""Initialize with environment variables."""

		#NOTE: Environment variables
		self.github_token = os.environ.get("GITHUB_TOKEN")
		self.repo_name = os.environ.get("REPO_NAME")
		self.pr_number = os.environ.get("PR_NUMBER")
		self.changelog_dir = os.environ.get("CHANGELOG_DIR", "changelog")
		self.client_subdir = os.environ.get("CLIENT_SUBDIR", "client")
		self.internal_subdir = os.environ.get("INTERNAL_SUBDIR", "internal")
		self.should_commit_changes = os.environ.get("COMMIT_CHANGES", "true").lower() == "true"
		self.commit_message_template = os.environ.get("COMMIT_MESSAGE", "Update changelog for PR #{pr_number}")

		#NOTE: Unified changelog settings
		self.unified_changelog = os.environ.get("UNIFIED_CHANGELOG", "false").lower() == "true"
		self.unified_format = os.environ.get("UNIFIED_FORMAT", "client").lower()

		#NOTE: Single file changelog settings
		self.single_file = os.environ.get("SINGLE_FILE", "false").lower() == "true"
		self.single_filename = os.environ.get("SINGLE_FILENAME", "CHANGELOG.md")

		#NOTE: Version display settings
		self.include_date_in_version = os.environ.get("INCLUDE_DATE_IN_VERSION", "true").lower() == "true"
		self.date_format = os.environ.get("DATE_FORMAT", "%Y-%m-%d")

		self._validate_env()

		self.gh = Github(self.github_token)
		self.repo = self.gh.get_repo(self.repo_name)

		#NOTE: Current date for use throughout the class
		self.today = datetime.now().strftime(self.date_format)

	def _validate_env(self):
		"""Validate that required environment variables are set."""
		if not self.github_token:
			logger.error("Error: GITHUB_TOKEN environment variable not set")
			sys.exit(1)

		if not self.repo_name or not self.pr_number:
			logger.error("Error: REPO_NAME or PR_NUMBER environment variables not set")
			sys.exit(1)

	def setup_directories(self):
		"""Create changelog directories if they don't exist."""
		changelog_dir = Path(self.changelog_dir)
		changelog_dir.mkdir(exist_ok=True)

		if not self.unified_changelog and not self.single_file:
			#NOTE: Create directories for different changelog types
			(changelog_dir / self.client_subdir).mkdir(exist_ok=True)
			(changelog_dir / self.internal_subdir).mkdir(exist_ok=True)

		return changelog_dir

	def get_pr_description(self):
		"""Fetch PR description from GitHub."""
		try:
			pr = self.repo.get_pull(int(self.pr_number))
			logger.info(f"Successfully fetched PR #{self.pr_number}")
			return pr.body, pr.title
		except Exception as e:
			logger.error(f"Error fetching PR #{self.pr_number}: {e}")
			return None, None

	def extract_target_version(self, description):
		"""Extract target version from PR description."""
		version_pattern = r"## Target Version\s+[`\[]?([vV]?\d+\.\d+\.\d+(?:-[a-zA-Z0-9.]+)?)[`\]]?"
		match = re.search(version_pattern, description, re.MULTILINE)

		if match:
			version = match.group(1)
			#NOTE: Normalize version format (ensure v prefix)
			if not version.startswith("v"):
				logger.warning("Version format without 'v' prefix detected, adding 'v'")
				version = f"v{version}"
			logger.info(f"Found target version: {version}")
			return version

		#NOTE Default to "notarget" if no version found
		logger.warning("No target version found, using 'notarget'")
		return "notarget"

	def get_version_with_date(self, version):
		"""Format the version with date if enabled."""
		if self.include_date_in_version:
			return f"{version} ({self.today})"
		return version

	def extract_changelog_section(self, description, section_name):
		"""Extract a specific changelog section from PR description."""
		pattern = rf"### {section_name}\s+(.+?)(?=\s+---|\s+###|\Z)"
		match = re.search(pattern, description, re.DOTALL | re.MULTILINE)

		if not match:
			logger.warning(f"No '{section_name}' section found in PR description")
			return []

		content = match.group(1).strip()

		#NOTE: Extract bullet points and format them
		items = []
		for line in content.split("\n"):
			#NOTE: Skip empty lines and HTML comments
			if not line.strip() or line.strip().startswith("<!--"):
				continue

			#NOTE: Extract actual content from bullet points
			bullet_match = re.search(r"\*\*([^:]+)\*\*:\s*\[?([^\]].+)", line.strip())
			if bullet_match:
				category = bullet_match.group(1).strip()
				text = bullet_match.group(2).strip()
				#NOTE: Remove closing brackets if present
				text = re.sub(r'\]$', '', text).strip()

				if text and not text.lower() == "[none]":
					items.append({"category": category, "text": text})

		logger.info(f"Extracted {len(items)} items from '{section_name}' section")
		return items

	def extract_related_issues(self, description):
		"""Extract related issues from PR description."""
		pattern = r"## Related Issues\s+(.+?)(?=\s+---|\s+##|\Z)"
		match = re.search(pattern, description, re.DOTALL | re.MULTILINE)

		if not match:
			return []

		content = match.group(1).strip()
		issues = []

		#NOTE: Look for issue numbers
		for line in content.split("\n"):
			if not line.strip():
				continue

			#NOTE: Find issue references like "Closes #123" or just "#123"
			issue_matches = re.findall(r'#(\d+)', line)
			issues.extend(issue_matches)

			#NOTE: Find JIRA-style references like "PROJECT-123"
			jira_matches = re.findall(r'([A-Z]+-\d+)', line)
			issues.extend(jira_matches)

		return issues

	def update_changelog_file(self, changelog_dir, version, section_type, changes, pr_number, pr_title, related_issues=None):
		"""Update the appropriate changelog file with new changes."""
		raw_version = version
		version_with_date = self.get_version_with_date(version)

		#NOTE: Determine file path based on type and version
		if self.single_file:
			#NOTE: Use a single file for all changes
			file_path = changelog_dir / self.single_filename
		elif self.unified_changelog:
			#NOTE: Use a unified file per version (use raw version for filename)
			file_path = changelog_dir / f"{raw_version}.md"
		else:
			#NOTE Use separate files per version and type (use raw version for filename)
			subdir = self.client_subdir if section_type == "client" else self.internal_subdir
			file_path = changelog_dir / subdir / f"{raw_version}.md"

		#NOTE: Create file with header if it doesn't exist
		if not file_path.exists():
			with open(file_path, "w") as f:
				if self.single_file:
					f.write("# Changelog\n\n")
				elif self.unified_changelog:
					f.write(f"# {version_with_date} Changelog\n\n")
				else:
					if section_type == "client":
						f.write(f"# {version_with_date}\n\n")
					else:
						f.write(f"# {version_with_date} Internal Changelog\n\n")
			logger.info(f"Created new changelog file: {file_path}")

		#NOTE: Read existing content
		with open(file_path, "r") as f:
			content = f.read()

		changes_by_category = {}
		for change in changes:
			category = change["category"]
			if category not in changes_by_category:
				changes_by_category[category] = []
			changes_by_category[category].append(change["text"])

		new_content = content.rstrip()

		if self.single_file:
			version_header = f"## {version_with_date}"
			version_pattern = f"## {re.escape(raw_version)}\\s*(?:\\([^)]+\\))?"

			if not re.search(version_pattern, content):
				new_content += f"\n\n{version_header}\n"

			if section_type == "client":
				pass
			else:
				new_content += f"\n\n### PR #{pr_number}: {pr_title}\n"
		elif section_type == "client":
			pass
		else:
			new_content += f"\n\n## PR #{pr_number}: {pr_title}\n"

		if (section_type != "client" or self.single_file) and related_issues:
			new_content += "\n**Related Issues:** "
			new_content += ", ".join(related_issues)
			new_content += "\n"

		for category, items in changes_by_category.items():
			heading_prefix = "###" if self.single_file else "##"
			new_content += f"\n{heading_prefix} {category}\n\n"
			for item in items:
				new_content += f"- {item}\n"

		with open(file_path, "w") as f:
			f.write(new_content)

		logger.info(f"Updated changelog for {version} using {section_type} format")
		return file_path

	def commit_changes(self, files_to_commit):
		"""Commit changes to the repository using Git commands."""
		if not self.should_commit_changes or not files_to_commit:
			logger.info("Skipping commit: either commit_changes is disabled or no files to commit")
			return

		try:
			commit_message = self.commit_message_template.replace("{pr_number}", self.pr_number)
			logger.info(f"Preparing to commit with message: {commit_message}")

			files_list = []
			for file_path in files_to_commit:
				if isinstance(file_path, Path):
					file_path = str(file_path)

				files_list.append(file_path)

			logger.info(f"Files to commit: {files_list}")

			#NOTE: Configure Git for GitHub Actions environment
			commands = [
				'git config --global user.email "github-actions[bot]@users.noreply.github.com"',
				'git config --global user.name "github-actions[bot]"',
				'git config --global --add safe.directory /github/workspace'
			]

			for cmd in commands:
				logger.info(f"Running: {cmd}")
				exit_code = os.system(cmd)
				if exit_code != 0:
					logger.warning(f"Command exited with code {exit_code}: {cmd}")

			for file_path in files_list:
				add_cmd = f'git add "{file_path}"'
				logger.info(f"Running: {add_cmd}")
				os.system(add_cmd)

			status_cmd = 'git status --porcelain'
			status_output = subprocess.check_output(status_cmd, shell=True).decode('utf-8').strip()

			if status_output:
				commit_cmd = f'git commit -m "{commit_message}"'
				logger.info(f"Running: {commit_cmd}")
				exit_code = os.system(commit_cmd)

				if exit_code != 0:
					logger.warning(f"Git commit exited with code {exit_code}")
				else:
					push_cmd = 'git push'
					logger.info(f"Running: {push_cmd}")
					exit_code = os.system(push_cmd)

					if exit_code != 0:
						logger.warning(f"Git push exited with code {exit_code}")
					else:
						logger.info("Successfully committed and pushed changes")
			else:
				logger.info("No changes detected to commit")

		except Exception as e:
			logger.error(f"Error committing changes: {e}")
			logger.error(traceback.format_exc())

	def run(self):
		"""Main execution method."""
		#NOTE: Setup directories
		changelog_dir = self.setup_directories()

		#NOTE: Get PR description
		description, pr_title = self.get_pr_description()
		if not description:
			logger.error("Error: Could not fetch PR description")
			sys.exit(1)

		#NOTE: Extract target version
		version = self.extract_target_version(description)

		#NOTE: Extract changelog sections
		client_changes = self.extract_changelog_section(description, "Client-Facing Changes")
		internal_changes = self.extract_changelog_section(description, "Internal Changes")
		related_issues = self.extract_related_issues(description)

		#NOTE: Track files that were updated
		updated_files = []

		if self.unified_changelog or self.single_file:
			#NOTE: Unified or single file changelog approach
			logger.info(f"Using {'single file' if self.single_file else 'unified'} changelog format")

			all_changes = []
			if client_changes:
				all_changes.extend(client_changes)
			if internal_changes:
				all_changes.extend(internal_changes)

			if all_changes:
				format_type = self.unified_format
				if format_type not in ["client", "internal"]:
					logger.warning(f"Unknown unified format '{format_type}', defaulting to 'client'")
					format_type = "client"

				file_path = self.update_changelog_file(
					changelog_dir, version, format_type, all_changes, self.pr_number, pr_title, related_issues
				)
				updated_files.append(file_path)
			else:
				logger.info("No changes found to add to changelog")
		else:
			#NOTE: Separate changelogs for client and internal changes
			if client_changes:
				file_path = self.update_changelog_file(
					changelog_dir, version, "client", client_changes, self.pr_number, pr_title, related_issues
				)
				updated_files.append(file_path)
			else:
				logger.info("No client-facing changes found")

			if internal_changes:
				file_path = self.update_changelog_file(
					changelog_dir, version, "internal", internal_changes, self.pr_number, pr_title, related_issues
				)
				updated_files.append(file_path)
			else:
				logger.info("No internal changes found")

		#NOTE: Commit changes if needed
		if self.should_commit_changes:
			self.commit_changes(updated_files)

		logger.info("Changelog generation completed successfully")


if __name__ == "__main__":
	generator = ChangelogGenerator()
	generator.run()
