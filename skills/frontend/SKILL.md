# Frontend Development Skill - MileSync

## Description
Specialized skill for developing React TypeScript frontend components following MileSync patterns.

## Expertise Areas
- React 18 with TypeScript
- TailwindCSS styling
- React Query for server state management
- React Router for navigation
- Custom hooks for logic extraction

## Code Style
- Functional components only
- Custom hooks for shared/reusable logic
- Type all props, state, and function parameters
- Max 500 lines per file
- Feature-based folder organization

## File Structure Pattern
```
frontend/src/
├── pages/           # Route page components
├── components/      # UI components by feature
│   ├── common/      # Shared components
│   ├── goals/       # Goal-related components
│   ├── tasks/       # Task components
│   └── dashboard/   # Dashboard widgets
├── hooks/           # Custom React hooks
├── api/             # API client functions
├── context/         # React context providers
├── types/           # TypeScript interfaces
└── utils/           # Utility functions
```

## Validation Commands
```bash
npm run lint
npm run build
```

## Example Usage
See `examples/react-query-hook.ts` for data fetching patterns.

## Common Gotchas
- Always handle loading and error states
- Use React Query for server state, Context for auth state
- Type all API responses
- Handle token refresh/expiry in API client interceptors
