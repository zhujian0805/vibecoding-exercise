import React from 'react';
import { Link, useLocation } from 'react-router-dom';

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
            <h2>GitHub OAuth Demo</h2>
          </Link>
        </div>
        
        <ul className="nav-menu">
          <li className={location.pathname === '/' ? 'active' : ''}>
            <Link to="/">Home</Link>
          </li>
          {isAuthenticated && (
            <>
              <li className={location.pathname === '/profile' ? 'active' : ''}>
                <Link to="/profile">User Profile</Link>
              </li>
              <li className={location.pathname === '/repositories' ? 'active' : ''}>
                <Link to="/repositories">Repositories</Link>
              </li>
            </>
          )}
        </ul>
        
        {isAuthenticated && user && (
          <div className="nav-user">
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
      </div>
    </nav>
  );
};

export default Navigation;
