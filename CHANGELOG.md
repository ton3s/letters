# Changelog

All notable changes to this project will be documented in this file.

## [2.4.0] - 2025-07-10

### Added
- Comprehensive Architecture Guide documenting system design
- In-depth Agent System Guide explaining multi-agent collaboration
- Code Improvements document with prioritized recommendations
- Detailed code review findings and best practices

### Documentation
- Created ARCHITECTURE.md with complete system overview
- Created AGENT_SYSTEM_GUIDE.md focusing on agent implementation
- Created CODE_IMPROVEMENTS.md with actionable improvements
- Updated README with links to new documentation

## [2.3.0] - 2025-07-10

### Changed
- Reorganized test structure - tests now live with their respective projects
- Moved CLI tests to `cli-tool/tests/`
- Removed duplicate API tests from root `/tests` folder
- Updated UI test file with proper authentication mocking
- Created component test structure for UI

### Added
- Test documentation for CLI tool
- Example component test for LoginButton
- Manual test directory for API integration tests

### Removed
- Root `/tests` folder - tests now organized by project

## [2.2.0] - 2025-07-10

### Added
- Single Sign-On (SSO) authentication with Microsoft Entra ID
- JWT token validation middleware for API security
- User profile display and authentication UI components
- Azure API Management configuration and policies
- Rate limiting and quota management per user
- Comprehensive authentication setup documentation
- Production deployment guide with APIM integration

### Changed
- API now requires authentication for all endpoints except health check
- Function App authorization changed from FUNCTION to ANONYMOUS (letting Entra ID handle auth)
- Letters now store user information (ID, email, name) for user-specific queries
- Frontend routes are now protected and require authentication

### Security
- Added proper CORS configuration for authentication flows
- Implemented token-based API authentication
- Added security headers in APIM responses
- Configured rate limiting to prevent abuse

## [2.1.0] - 2025-07-10

### Added
- Comprehensive unit test suite for API with 80%+ code coverage
- Test runner script with coverage reporting
- Integration tests for complete workflows
- Detailed test documentation

### Changed
- Refactored codebase into organized directory structure:
  - `api/` - Azure Functions backend
  - `ui/` - React frontend application  
  - `cli-tool/` - Command line interface
- Updated all documentation to reflect new structure
- Enhanced setup script for new directory layout

## [2.0.0] - 2025-07-10

### Added
- React UI with modern, responsive design
- Company profile management for pre-filling information
- Smart placeholder detection and editing system
- Letter history with search and filtering
- Real-time progress tracking during generation
- Auto-save functionality for letter edits
- Mobile-responsive design

### Changed
- Removed authentication system for simplified access
- Reorganized UI to focus on core features
- Enhanced agent conversation display
- Improved letter formatting and display

### Fixed
- CORS configuration for local development
- Agent name spacing in progress indicators
- Placeholder replacement logic
- Signature formatting issues

## [1.0.0] - 2025-07-09

### Added
- Initial release with Azure Functions API
- Multi-agent letter generation system
- Three specialized AI agents (Writer, Compliance, Customer Service)
- Support for 8 letter types
- Cosmos DB integration for persistence
- CLI tool for testing
- Comprehensive API documentation