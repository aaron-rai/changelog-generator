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
	try:
		project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
		sys.path.insert(0, project_root)

		from src.generate_changelog import ChangelogGenerator
	except ImportError as e:
		logger.error(f"Could not import ChangelogGenerator: {e}")
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
				self.should_commit_changes = False
				self.commit_message_template = "Update changelog for PR #{pr_number}"

				self.unified_changelog = False
				self.unified_format = "client"  #NOTE: Options: "client" or "internal"

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

		generator.run()

		changelog_files = os.listdir(generator.changelog_dir)
		logger.info(f"Files in changelog directory: {changelog_files}")

		version = generator.extract_target_version(MOCK_PR_DESCRIPTION)
		if generator.unified_changelog:
			file_path = os.path.join(generator.changelog_dir, f"{version}.md")
			if os.path.exists(file_path):
				with open(file_path, "r") as f:
					content = f.read()
				logger.info(f"\nContent of unified changelog {file_path}:\n{'-' * 40}\n{content}\n{'-' * 40}")
			else:
				logger.error(f"Unified changelog file not found: {file_path}")
		else:
			client_file_path = os.path.join(generator.changelog_dir, generator.client_subdir, f"{version}.md")
			internal_file_path = os.path.join(generator.changelog_dir, generator.internal_subdir, f"{version}.md")

			if os.path.exists(client_file_path):
				with open(client_file_path, "r") as f:
					content = f.read()
				logger.info(f"\nContent of client changelog {client_file_path}:\n{'-' * 40}\n{content}\n{'-' * 40}")
			else:
				logger.error(f"Client changelog file not found: {client_file_path}")

			if os.path.exists(internal_file_path):
				with open(internal_file_path, "r") as f:
					content = f.read()
				logger.info(f"\nContent of internal changelog {internal_file_path}:\n{'-' * 40}\n{content}\n{'-' * 40}")
			else:
				logger.error(f"Internal changelog file not found: {internal_file_path}")

		logger.info("Test completed successfully!")

	finally:
		cleanup_test_environment(temp_dir, original_dir)


if __name__ == "__main__":
	run_test()
