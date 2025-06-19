import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import ThemeToggle from './ThemeToggle';

interface User {
  login: string;
  name: string;
  avatar_url: string;
}

interface NavigationProps {
  isAuthenticated: boolean;
  user: User | null;
  onLogout: () => void;
}

const Navigation: React.FC<NavigationProps> = ({ isAuthenticated, user, onLogout }) => {
  const location = useLocation();

  return (
    <nav className="navigation">
      <div className="nav-container">
        <div className="nav-brand">
          <Link to="/">
            <h2>Vibecoding Exercise</h2>
          </Link>
        </div>
        
        <ul className="nav-menu">
          <li className={location.pathname === '/' ? 'active' : ''}>
            <Link to="/">Home</Link>
          </li>
          {isAuthenticated && (
            <>
              <li className={location.pathname === '/profile' ? 'active' : ''}>
                <Link to="/profile">Profile</Link>
              </li>
              <li className={location.pathname === '/repositories' ? 'active' : ''}>
                <Link to="/repositories">Repositories</Link>
              </li>
              <li className={location.pathname === '/following' ? 'active' : ''}>
                <Link to="/following">Following</Link>
              </li>
              <li className={location.pathname === '/followers' ? 'active' : ''}>
                <Link to="/followers">Followers</Link>
              </li>
              <li className={location.pathname === '/gists' ? 'active' : ''}>
                <Link to="/gists">Gists</Link>
              </li>
              <li className={location.pathname === '/pullrequests' ? 'active' : ''}>
                <Link to="/pullrequests">Pull Requests</Link>
              </li>
            </>
          )}
        </ul>
        
        {isAuthenticated && user && (
          <div className="nav-user">
            <ThemeToggle />
            <img 
              src={user.avatar_url} 
              alt="Avatar" 
              className="nav-avatar"
            />
            <span className="nav-username">{user.name || user.login}</span>
            <button onClick={onLogout} className="logout-btn">
              Logout
            </button>
          </div>
        )}
        
        {!isAuthenticated && (
          <div className="nav-actions">
            <ThemeToggle />
          </div>
        )}
      </div>
    </nav>
  );
};

export default Navigation;
