#!/usr/bin/env python3
"""
Local Test Script for Changelog Generator

This script creates a mock PR description and tests the changelog generator
without requiring an actual GitHub repository or PR.
"""

import os
import sys
import tempfile
import shutil
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('changelog-test')

# Mock PR data
MOCK_PR_DESCRIPTION = """
# Pull Request

## Summary

This is a test PR for the changelog generator.

---

## Change Log

### Client-Facing Changes

<!-- Use plain, non-technical language for stakeholders or clients -->
- **Added**: New login page with improved security features
- **Changed**: Updated dashboard layout for better usability
- **Removed**: Legacy reporting feature that was replaced in v2.0
- **Fixed**: Issue with password reset emails not being delivered

### Internal Changes

<!-- Use technical detail for devs or contributors -->
- **Added**: Authentication service with JWT implementation
- **Changed**: Refactored user repository for better performance
- **Deprecated**: Old API endpoints (v1) to be removed in next version
- **Removed**: Unused database migrations
- **Fixed**: Race condition in concurrent user updates
- **Security**: Implemented rate limiting on authentication endpoints

---

## Target Version
v2.1.0

---

## Related Issues

<!-- Link related issues or tickets -->
#123
JIRA-456

---

## Checklist

- [x] Pulled latest changes from the target branch
- [x] Resolved conflicts
- [x] Tested locally
- [x] Code and docs updated
- [x] Passed all linting/tests (`pre-commit run --all-files`)

---

## Notes

This is a test PR for local testing.
"""

MOCK_PR_TITLE = "Implement new authentication system"
MOCK_PR_NUMBER = "999"


class MockPR:
	"""Mock Pull Request object with the minimum required attributes."""

	def __init__(self, body, title):
		self.body = body
		self.title = title


class MockRepo:
	"""Mock Repository object that returns our mock PR."""

	def __init__(self, mock_pr):
		self.mock_pr = mock_pr

	def get_pull(self, number):
		return self.mock_pr


def setup_test_environment():
	"""Set up a temporary directory for testing."""
	temp_dir = tempfile.mkdtemp()
	logger.info(f"Created temporary directory: {temp_dir}")

	original_dir = os.getcwd()
	os.chdir(temp_dir)

	return temp_dir, original_dir


def cleanup_test_environment(temp_dir, original_dir):
	"""Clean up the temporary directory."""
	os.chdir(original_dir)
	shutil.rmtree(temp_dir)
	logger.info(f"Removed temporary directory: {temp_dir}")


def run_test():
	"""Run the changelog generator test."""
	#NOTE: Import the generator class
	#NOTE: Adjust the import path based on your project structure
	sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
	try:
		from src.generate_changelog import ChangelogGenerator
	except ImportError:
		logger.error("Could not import ChangelogGenerator. Make sure the script is in the correct location.")
		sys.exit(1)

	temp_dir, original_dir = setup_test_environment()

	try:
		mock_pr = MockPR(MOCK_PR_DESCRIPTION, MOCK_PR_TITLE)
		mock_repo = MockRepo(mock_pr)

		class TestChangelogGenerator(ChangelogGenerator):

			def __init__(self):
				#NOTE: Initialize without environment variables
				self.github_token = "fake-token"
				self.repo_name = "test/repo"
				self.pr_number = MOCK_PR_NUMBER
				self.changelog_dir = "changelog"
				self.client_subdir = "client"
				self.internal_subdir = "internal"
				self.commit_changes = False
				self.commit_message_template = "Update changelog for PR #{pr_number}"
				self.gh = None
				self.repo = mock_repo

			def get_pr_description(self):
				"""Override to return our mock PR data."""
				return MOCK_PR_DESCRIPTION, MOCK_PR_TITLE

			def commit_changes(self, files_to_commit):
				"""Override to prevent actual git operations."""
				logger.info(f"Would commit these files: {files_to_commit}")
				return

		generator = TestChangelogGenerator()

		changelog_dir = generator.setup_directories()

		version = generator.extract_target_version(MOCK_PR_DESCRIPTION)
		client_changes = generator.extract_changelog_section(MOCK_PR_DESCRIPTION, "Client-Facing Changes")
		internal_changes = generator.extract_changelog_section(MOCK_PR_DESCRIPTION, "Internal Changes")
		related_issues = generator.extract_related_issues(MOCK_PR_DESCRIPTION)

		updated_files = []

		if client_changes:
			file_path = generator.update_changelog_file(
				changelog_dir, version, "client", client_changes, generator.pr_number, MOCK_PR_TITLE, related_issues
			)
			updated_files.append(file_path)

		if internal_changes:
			file_path = generator.update_changelog_file(
				changelog_dir, version, "internal", internal_changes, generator.pr_number, MOCK_PR_TITLE, related_issues
			)
			updated_files.append(file_path)

		logger.info(f"Generated {len(updated_files)} changelog files:")
		for file_path in updated_files:
			logger.info(f"- {file_path}")

			with open(file_path, "r") as f:
				content = f.read()

			logger.info(f"\nContent of {file_path}:\n{'-' * 40}\n{content}\n{'-' * 40}")

		logger.info("Test completed successfully!")

	finally:
		cleanup_test_environment(temp_dir, original_dir)


if __name__ == "__main__":
	run_test()
