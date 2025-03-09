# Memory Machine Project - File Architecture

This document provides a high-level overview of the file organization for the Memory Machine project.

## Root Directory

- `README.md` - Project introduction and getting started guide
- `package.json` - Project dependencies and scripts
- `tsconfig.json` - TypeScript configuration
- `.gitignore` - Git ignore file
- `.eslintrc.js` - ESLint configuration
- `.prettierrc` - Prettier configuration

## Source Code

### `/src` - Main source code directory

- `/components` - React components
  - `/common` - Reusable components
  - `/layout` - Layout components
  - `/memory` - Memory-specific components
  
- `/hooks` - Custom React hooks

- `/pages` - Page components
  - `/auth` - Authentication pages
  - `/dashboard` - Dashboard pages
  - `/memory` - Memory pages

- `/services` - Service layer for API calls
  - `/api` - API client and utilities
  - `/memory` - Memory-related services

- `/utils` - Utility functions and helpers

- `/types` - TypeScript type definitions

- `/styles` - Global styles and theming

- `/constants` - Application constants

## Backend

### `/server` - Backend code

- `/controllers` - Request handlers
- `/models` - Data models
- `/routes` - API routes
- `/middleware` - Express middleware
- `/db` - Database configuration and connection
- `/utils` - Server utility functions

## Configuration

### `/config` - Configuration files

- `/dev` - Development configuration
- `/prod` - Production configuration
- `/test` - Test configuration

## Tests

### `/tests` - Test files

- `/unit` - Unit tests
- `/integration` - Integration tests
- `/e2e` - End-to-end tests

## Documentation

### `/docs` - Documentation files

- `/api` - API documentation
- `/architecture` - Architecture documentation
- `/user-guides` - User guides

## Build and Deployment

### `/build` - Build output directory

### `/scripts` - Build and deployment scripts

## Public

### `/public` - Public assets

- `/images` - Image assets
- `/fonts` - Font files
- `/icons` - Icon assets

## GitHub

### `/.github` - GitHub-specific files

- `/workflows` - GitHub Actions workflows
- `copilot-instructions.md` - Instructions for GitHub Copilot
