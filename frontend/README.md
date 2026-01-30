# Sichelgaita.AI Frontend

Next.js 14 frontend application for the Sichelgaita.AI Data Wealth Platform.

## Features

- **Next.js 14**: App Router with React Server Components
- **TypeScript**: Full type safety across the application
- **Tailwind CSS**: Utility-first CSS framework
- **Shadcn/ui**: High-quality, accessible component library
- **Radix UI**: Unstyled, accessible UI primitives
- **Lucide React**: Beautiful, consistent icons
- **date-fns**: Modern date utility library

## Design System

- **Typography**: Inter (sans-serif) for UI, Merriweather (serif) for reports
- **Color Palette**: Neutral grays with primary blue accent
- **Style**: Investment Bank meets Modern SaaS aesthetic

## Setup

### Prerequisites

- Node.js 18.17.0+
- npm 9.0.0+

### Installation

```bash
# Install dependencies
npm install

# Copy environment file
cp .env.local.example .env.local
# Edit .env.local with your configuration
```

## Development

### Run the development server

```bash
npm run dev

# The application will be available at:
# http://localhost:3000
```

### Build for production

```bash
# Create optimized production build
npm run build

# Run production server
npm run start
```

### Code Quality

```bash
# Lint code
npm run lint

# Format code (if configured)
npm run format
```

## Project Structure

```
frontend/
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx         # Root layout with fonts
│   │   ├── page.tsx           # Landing page
│   │   ├── workspace/         # Workspace page
│   │   └── globals.css        # Global styles
│   ├── components/
│   │   ├── ui/                # Shadcn/ui components
│   │   │   ├── button.tsx
│   │   │   ├── card.tsx
│   │   │   ├── dialog.tsx
│   │   │   ├── input.tsx
│   │   │   ├── progress.tsx
│   │   │   └── scroll-area.tsx
│   │   └── workspace/         # Workspace-specific components
│   │       ├── FileUploader.tsx
│   │       ├── FileCard.tsx
│   │       └── ProjectSidebar.tsx
│   ├── lib/
│   │   ├── api.ts             # Backend API client
│   │   └── utils.ts           # Utility functions
│   └── types/
│       └── index.ts           # TypeScript type definitions
├── public/                     # Static assets
├── components.json             # Shadcn/ui configuration
├── tailwind.config.ts          # Tailwind CSS configuration
├── tsconfig.json              # TypeScript configuration
└── package.json
```

## Key Components

### Workspace Page
Located at `/workspace`, provides a 3-column layout:
- **Left Sidebar**: Project navigation and management
- **Center Canvas**: File uploader and file grid
- **Right Panel**: File details and metadata

### FileUploader
Drag-and-drop file upload component with:
- HTML5 native drag-drop API
- Client-side validation (file type, size)
- Progress tracking with visual feedback
- Supported formats: CSV, Excel, PDF, Images (max 50MB)

### FileCard
Displays file metadata with:
- File type icons (Lucide React)
- Status badges (completed, processing, failed, uploading)
- AI-generated summaries
- Relative timestamps

## API Integration

The frontend communicates with the FastAPI backend via REST API:

```typescript
// API Client: src/lib/api.ts
import { uploadFile, getFileMetadata, listProjectFiles } from '@/lib/api';

// Upload a file
const response = await uploadFile(file, projectId);

// Get file metadata
const metadata = await getFileMetadata(fileId);

// List project files
const files = await listProjectFiles(projectId);
```

### Environment Variables

```bash
# .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Type System

All types are defined in `src/types/index.ts`:

- **FileMetadata**: File information from backend
- **FileType**: Union type ('csv' | 'excel' | 'pdf' | 'image')
- **Project**: Project metadata
- **FileUploadResponse**: Upload API response
- **UploadProgress**: Client-side upload state

## Styling Guidelines

- Use Tailwind utility classes for styling
- Follow Shadcn/ui component patterns
- Maintain neutral color palette (grays with blue accent)
- Ensure responsive design (mobile-first approach)
- Add ARIA labels for accessibility

## Development Workflow

1. **Create components** in `src/components/`
2. **Define types** in `src/types/index.ts`
3. **Add API calls** in `src/lib/api.ts`
4. **Use utilities** from `src/lib/utils.ts`
5. **Style with Tailwind** using the `cn()` utility for conditional classes

## Adding Shadcn/ui Components

```bash
# Install a new component (example: toast)
npx shadcn-ui@latest add toast
```

## Browser Support

- Modern browsers with ES6+ support
- Chrome, Firefox, Safari, Edge (latest versions)

## Performance

- Server Components for initial load optimization
- Client Components only where interactivity is needed
- Image optimization with Next.js Image component
- Code splitting with dynamic imports (future)

## Troubleshooting

### Port already in use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill
```

### Module not found errors
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript errors
```bash
# Restart TypeScript server in VS Code
Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server"
```

## Backend Integration

This frontend connects to the FastAPI backend at `http://localhost:8000`.
Ensure the backend is running before testing file uploads.

See [backend README](../backend/README.md) for backend setup instructions.
