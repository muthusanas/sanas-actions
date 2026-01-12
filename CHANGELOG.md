# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
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
