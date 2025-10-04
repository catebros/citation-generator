# Citation Generator Frontend

A React + TypeScript + TailwindCSS frontend for the Citation Generator project.

## Features

- **Project Management**: Create, edit, and delete citation projects
- **Citation CRUD**: Full create, read, update, delete operations for citations
- **Multiple Citation Types**: Book, Article, Website, Report with type-specific fields
- **Bibliography Generation**: Generate APA and MLA format bibliographies
- **Safe HTML Rendering**: Secure rendering of formatted citations with DOMPurify
- **Responsive Design**: Mobile-friendly interface with TailwindCSS
- **Toast Notifications**: User feedback with react-hot-toast
- **Loading States**: Proper loading and error handling
- **Type Safety**: Full TypeScript support

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development and building
- **TailwindCSS** for styling
- **React Router DOM** for navigation
- **Axios** for API calls
- **Framer Motion** for animations
- **React Hot Toast** for notifications
- **DOMPurify** for safe HTML rendering
- **Heroicons** for icons

## Project Structure

```
frontend/
├── src/
│   ├── api/           # API client and functions
│   ├── components/    # Reusable UI components
│   ├── hooks/         # Custom React hooks
│   ├── pages/         # Page components
│   ├── types/         # TypeScript type definitions
│   ├── App.tsx        # Main application component
│   ├── main.tsx       # Application entry point
│   └── index.css      # Global styles and TailwindCSS imports
├── package.json       # Dependencies and scripts
├── tailwind.config.js # TailwindCSS configuration
├── vite.config.ts     # Vite configuration
└── tsconfig.json      # TypeScript configuration
```

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

## Development

1. **Start the development server:**
   ```bash
   npm run dev
   ```

2. **The application will be available at:**
   ```
   http://localhost:3000
   ```

3. **Make sure the backend API is running at:**
   ```
   http://localhost:8000
   ```

## Build for Production

1. **Build the application:**
   ```bash
   npm run build
   ```

2. **Preview the production build:**
   ```bash
   npm run preview
   ```

## API Integration

The frontend connects to the FastAPI backend through REST endpoints:

- **Projects**: `/projects` (GET, POST, PUT, DELETE)
- **Citations**: `/projects/{id}/citations` (GET, POST, PUT, DELETE)
- **Bibliography**: `/projects/{id}/bibliography?format_type=apa|mla` (GET)

## Key Components

### Pages
- **HomePage**: Project list with create project functionality
- **ProjectPage**: Project details, citations table, and bibliography generation

### Components
- **ProjectCard**: Displays project information or create project option
- **CitationTable**: Displays citations in a responsive table
- **CitationFormModal**: Dynamic form for creating/editing citations
- **BibliographyModal**: Generate and display APA/MLA bibliographies
- **Modal**: Reusable modal component with animations
- **LoadingSpinner**: Loading indicator component
- **ConfirmDialog**: Confirmation dialog for destructive actions

### Hooks
- **useProjects**: Project CRUD operations and state management
- **useCitations**: Citation CRUD operations and state management
- **useBibliography**: Bibliography generation functionality

## Features in Detail

### Citation Form
- Dynamic form that changes fields based on citation type
- Type-specific validations and field requirements
- Author management with comma-separated input
- Year nullability option ("Year is None" checkbox)
- Real-time form validation

### Bibliography Generation
- Support for APA 7th edition and MLA 9th edition
- Safe HTML rendering with DOMPurify for italics and formatting
- Copy to clipboard functionality
- Format switching without regeneration

### Error Handling
- Comprehensive error handling for all API calls
- Toast notifications for success and error states
- Loading states for better UX
- Network error handling with fallback messages

### Responsive Design
- Mobile-first design approach
- Responsive grids and layouts
- Touch-friendly interface elements
- Optimized for various screen sizes

## Environment Variables

The application uses these default configurations:
- **API Base URL**: `http://localhost:8000`
- **Development Port**: `3000`

To modify these, update the configuration in:
- `src/api/index.ts` for API base URL
- `vite.config.ts` for development port

## Browser Support

- Modern browsers with ES2020 support
- Chrome 80+
- Firefox 72+
- Safari 13.1+
- Edge 80+

## Development Guidelines

1. **Code Style**: Follow TypeScript best practices
2. **Components**: Keep components small and focused
3. **State Management**: Use custom hooks for complex state
4. **Error Handling**: Always handle loading and error states
5. **Accessibility**: Ensure proper ARIA labels and keyboard navigation
6. **Performance**: Use React.memo and useMemo where appropriate

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure backend is running on `http://localhost:8000`
   - Check CORS configuration in backend
   - Verify network connectivity

2. **Build Errors**
   - Clear node_modules and reinstall: `rm -rf node_modules package-lock.json && npm install`
   - Update dependencies: `npm update`

3. **TypeScript Errors**
   - Ensure all dependencies are installed
   - Check TypeScript configuration in `tsconfig.json`
   - Verify import paths are correct

## License

This project is part of the Citation Generator application.