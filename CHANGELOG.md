# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- SQLite database module for persistent storage of settings, team members, and action items
- Frontend API client (src/api.js) with centralized error handling and FormData support
- Analytics API endpoint with team stats, pending items, and leaderboard
- Isolated test database fixture for reliable test execution
- 25 new tests for database module and analytics API (131 total, 97% coverage)
- FastAPI backend with Python 3.13 and UV package manager
- ExtractionService for Claude AI-powered action item parsing
- JiraService for REST API ticket creation with batch support
- SlackService for notifications with single/bulk send
- SettingsService for user settings and team member management
- API routes with file upload validation (10MB limit)
- Pydantic models for type-safe request/response handling
- Vue 3 application with Vite build system and Tailwind CSS
- Pinia stores for actions, settings, and notifications state management
- 9 Vue components: AppHeader, CreateTab, StepCard, ActionItem, SuccessState, HistoryTab, SettingsPanel, NotificationToast, MeetingInput
- Shared constants for timing and configuration values
- Utility functions for initials generation and unique value extraction
- MeetingInput component with paste text and file upload options
- Support for PDF, DOCX, MD, and TXT file uploads with drag-and-drop
- FILE_UPLOAD constants for accepted file types and size limits
- 65 unit tests with Vitest covering stores and utilities

### Changed
- Frontend stores now call backend APIs instead of using mock data
- Settings store auto-saves changes to backend with debouncing
- SettingsPage supports full team member CRUD with modal dialog
- AnalyticsPage fetches real data from backend analytics endpoint
- Refactored SettingsService to use SQLite instead of in-memory storage
- Migrated single-file HTML prototype to modular Vue.js architecture
- Extracted inline styles to Tailwind CSS utility classes
- Replaced Notion URL input with flexible text paste and file upload options

### Fixed
- SQLite compatibility: replaced PostgreSQL FILTER syntax with SUM/CASE
- FormData uploads: skip Content-Type header to allow browser multipart handling
