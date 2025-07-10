# AquaTrak Frontend

A modern React-based frontend application for the AquaTrak AI-GIS Water Risk Monitoring Platform.

## Features

- **Modern UI/UX**: Built with Material-UI for a professional, responsive design
- **Real-time Data**: Live updates and real-time monitoring capabilities
- **Interactive Dashboards**: Customizable dashboards with charts and metrics
- **Module Management**: Comprehensive module monitoring and configuration
- **Alert System**: Real-time alerts and notifications
- **Authentication**: Secure JWT-based authentication
- **Responsive Design**: Works on desktop, tablet, and mobile devices

## Tech Stack

- **React 18** - Modern React with hooks and functional components
- **TypeScript** - Type-safe development
- **Material-UI (MUI)** - Professional UI components
- **React Query** - Data fetching and caching
- **React Router** - Client-side routing
- **Zustand** - State management
- **Axios** - HTTP client
- **Recharts** - Data visualization
- **React Hook Form** - Form handling
- **React Hot Toast** - Notifications

## Prerequisites

- Node.js 16+ 
- npm or yarn
- Backend API running on `http://localhost:8000`

## Installation

1. **Navigate to the frontend directory:**
   ```bash
   cd src/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Create environment file:**
   ```bash
   cp .env.example .env
   ```

4. **Configure environment variables:**
   ```env
   REACT_APP_API_URL=http://localhost:8000
   REACT_APP_ENVIRONMENT=development
   ```

## Development

### Start Development Server

```bash
npm start
```

The application will be available at `http://localhost:3000`

### Build for Production

```bash
npm run build
```

### Run Tests

```bash
npm test
```

### Lint Code

```bash
npm run lint
npm run lint:fix
```

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Auth/           # Authentication components
│   ├── Common/         # Common UI components
│   └── Layout/         # Layout components
├── pages/              # Page components
│   ├── Auth/           # Authentication pages
│   ├── Dashboard/      # Dashboard pages
│   ├── Modules/        # Module management pages
│   ├── Analysis/       # Analysis pages
│   ├── Alerts/         # Alert management pages
│   └── Settings/       # Settings pages
├── services/           # API services
│   └── api.ts          # Main API client
├── store/              # State management
│   └── authStore.ts    # Authentication store
├── types/              # TypeScript type definitions
│   └── api.ts          # API types
├── utils/              # Utility functions
├── hooks/              # Custom React hooks
└── App.tsx             # Main application component
```

## API Integration

The frontend connects to the backend through a comprehensive API layer:

### Authentication
- JWT-based authentication
- Automatic token refresh
- Protected routes
- User profile management

### Data Management
- Real-time data fetching with React Query
- Optimistic updates
- Error handling and retry logic
- Caching and background updates

### Modules
- IoT Water Consumption monitoring
- Environmental Health analysis
- Urban Green Space assessment
- Urban Water Network optimization
- And more...

## Key Components

### Dashboard
- Overview cards with key metrics
- Interactive charts and graphs
- Real-time data visualization
- Customizable widgets

### Module Management
- Module status monitoring
- Configuration management
- Performance metrics
- Health indicators

### Alert System
- Real-time alert notifications
- Severity-based filtering
- Alert acknowledgment and resolution
- Historical alert tracking

### Analysis
- Comprehensive analysis tools
- Result visualization
- Historical data comparison
- Export capabilities

## Authentication

The application uses JWT-based authentication with the following features:

- **Login/Logout**: Secure authentication flow
- **Token Management**: Automatic token refresh
- **Protected Routes**: Route-level security
- **User Roles**: Role-based access control
- **Session Persistence**: Remember user sessions

### Sample Users

For testing, the following users are available:

- **Admin**: `admin@aquatrak.com` / `admin123`
- **Manager**: `manager@aquatrak.com` / `manager123`
- **Analyst**: `analyst@aquatrak.com` / `analyst123`
- **Viewer**: `viewer@aquatrak.com` / `viewer123`

## State Management

The application uses Zustand for state management:

- **Auth Store**: Authentication state and user data
- **Global State**: Application-wide state
- **Local State**: Component-specific state with React hooks

## Styling

The application uses Material-UI with a custom theme:

- **Consistent Design**: Material Design principles
- **Responsive Layout**: Mobile-first approach
- **Custom Theme**: Branded color scheme
- **Dark/Light Mode**: Theme switching capability

## Performance

- **Code Splitting**: Lazy loading of routes
- **Memoization**: Optimized re-renders
- **Caching**: React Query for data caching
- **Bundle Optimization**: Tree shaking and minification

## Error Handling

- **Global Error Boundary**: Catches and handles errors
- **API Error Handling**: Consistent error responses
- **User Feedback**: Toast notifications for errors
- **Fallback UI**: Graceful degradation

## Testing

The application includes comprehensive testing:

- **Unit Tests**: Component and utility testing
- **Integration Tests**: API integration testing
- **E2E Tests**: End-to-end user flows
- **Accessibility Tests**: WCAG compliance

## Deployment

### Production Build

```bash
npm run build
```

### Environment Configuration

Set the following environment variables for production:

```env
REACT_APP_API_URL=https://api.aquatrak.com
REACT_APP_ENVIRONMENT=production
```

### Docker Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Ensure the backend is running on the correct port
   - Check CORS configuration
   - Verify API URL in environment variables

2. **Authentication Issues**
   - Clear browser storage
   - Check token expiration
   - Verify user credentials

3. **Build Errors**
   - Clear node_modules and reinstall
   - Check TypeScript errors
   - Verify all dependencies are installed

### Development Tips

- Use React Developer Tools for debugging
- Enable React Query DevTools for data debugging
- Use the browser's Network tab to monitor API calls
- Check the console for error messages

## Support

For support and questions:

- Check the documentation
- Review the troubleshooting guide
- Contact the development team
- Submit an issue on GitHub

## License

This project is proprietary to AquaTrak. Unauthorized use is strictly prohibited. 