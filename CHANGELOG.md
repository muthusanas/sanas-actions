# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- FastAPI backend with Python 3.13 and UV package manager
- ExtractionService for Claude AI-powered action item parsing
- JiraService for REST API ticket creation with batch support
- SlackService for notifications with single/bulk send
- SettingsService for user settings and team member management
- API routes with file upload validation (10MB limit)
- Pydantic models for type-safe request/response handling
- 108 backend tests with pytest at 96% code coverage
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
- Migrated single-file HTML prototype to modular Vue.js architecture
- Extracted inline styles to Tailwind CSS utility classes
- Replaced Notion URL input with flexible text paste and file upload options
