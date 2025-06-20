# GitHub OAuth Flow Demo

A complete OAuth authentication demo with a Flask backend and React frontend, showcasing the GitHub OAuth flow.

## Architecture

- **Backend**: Flask API server (port 5000) handling OAuth flow
- **Frontend**: React TypeScript application (port 80) with modern UI
- **Authentication**: GitHub OAuth 2.0 flow with session management

## Features

### Backend (Flask)
- GitHub OAuth 2.0 authentication
- Session management with cookies
- CORS enabled for frontend communication
- RESTful API endpoints for authentication status
- User profile data fetching from GitHub API

### Frontend (React)
- Modern, responsive UI with gradient background
- GitHub login with beautiful button design
- Real-time authentication status checking
- Complete user profile display with avatar
- GitHub stats (repositories, followers, following)
- Profile refresh and logout functionality
- Error handling with user-friendly messages
- Mobile-responsive design

## Quick Start

### Option 1: Use the Launch Script (Recommended)

1. **Set up GitHub OAuth App**:
   - Go to https://github.com/settings/developers
   - Click "New OAuth App"
   - Set Authorization callback URL to: `http://localhost:5000/api/callback`
   - Copy your Client ID and Client Secret

2. **Set environment variables**:
   ```bash
   export GITHUB_CLIENT_ID=your_github_client_id
   export GITHUB_CLIENT_SECRET=your_github_client_secret
   ```

3. **Run the demo**:
   ```bash
   ./start-demo.sh
   ```

4. **Access the application**:
   - Frontend: http://localhost (port 80)
   - Backend API: http://localhost:5000

### Option 2: Manual Setup

1. **Install backend dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install frontend dependencies**:
   ```bash
   cd frontend
   npm install
   ```

3. **Set environment variables**:
   ```bash
   export GITHUB_CLIENT_ID=your_github_client_id
   export GITHUB_CLIENT_SECRET=your_github_client_secret
   export FLASK_SECRET_KEY=your_flask_secret_key
   ```

4. **Start backend**:
   ```bash
   python oauth_backend.py
   ```

5. **Start frontend** (in another terminal):
   ```bash
   cd frontend
   sudo npm start  # Requires sudo to run on port 80
   ```

## API Endpoints

- `GET /api/user` - Check authentication status
- `GET /api/login` - Get GitHub OAuth URL
- `GET /api/callback` - Handle OAuth callback
- `POST /api/logout` - Logout user
- `GET /api/profile` - Get detailed user profile
- `GET /api/health` - Health check

## Project Structure

```
vibecoding-exercise/
├── oauth_backend.py       # Flask backend server
├── requirements.txt       # Python dependencies
├── start-demo.sh         # Launch script
├── README.md             # This file
└── frontend/             # React frontend
    ├── src/
    │   ├── App.tsx       # Main React component
    │   ├── App.css       # Styles
    │   └── ...
    ├── package.json      # Node.js dependencies
    └── ...
```

## Configuration

### Environment Variables

- `GITHUB_CLIENT_ID`: Your GitHub OAuth app client ID (required)
- `GITHUB_CLIENT_SECRET`: Your GitHub OAuth app client secret (required)
- `FLASK_SECRET_KEY`: Secret key for Flask sessions (optional, defaults to dev key)
- `FRONTEND_URL`: Frontend URL (optional, defaults to http://localhost)
- `BACKEND_PORT`: Backend port (optional, defaults to 5000)

### GitHub OAuth App Setup

1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Click "New OAuth App"
3. Fill in the application details:
   - **Application name**: Your app name
   - **Homepage URL**: http://localhost
   - **Authorization callback URL**: http://localhost:5000/api/callback
4. Save and copy the Client ID and Client Secret

## Security Features

- CSRF protection with Flask sessions
- CORS properly configured for frontend-backend communication
- Secure session cookie handling
- Environment-based configuration for secrets

## Development

### Frontend Development
The React app includes:
- TypeScript for type safety
- Axios for HTTP requests
- Modern CSS with animations and responsive design
- Error boundary and loading states

### Backend Development
The Flask API includes:
- RESTful endpoint design
- Session-based authentication
- GitHub API integration
- Error handling and validation

## Troubleshooting

1. **Port 80 access denied**: Run frontend with `sudo npm start`
2. **CORS errors**: Ensure backend is running and CORS is configured
3. **OAuth callback fails**: Check GitHub app callback URL matches `http://localhost:5000/api/callback`
4. **Environment variables**: Make sure `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET` are set

## Technologies Used

- **Backend**: Python, Flask, Flask-CORS, Requests
- **Frontend**: React, TypeScript, Axios, CSS3
- **Authentication**: GitHub OAuth 2.0
- **Development**: Node.js, npm, Create React App
