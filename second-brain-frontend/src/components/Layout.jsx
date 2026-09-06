import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export default function Layout({ children }) {
  const { email, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate('/login');
  }

  return (
    <div className="app-shell">
      <div className="topbar">
        <span className="brand">
          Second <span className="brand-mark">Brain</span>
        </span>
        <div className="topbar-right">
          {email && <span className="topbar-email">{email}</span>}
          <button className="logout-btn" onClick={handleLogout}>
            Log out
          </button>
        </div>
      </div>

      <nav className="tab-nav">
        <NavLink to="/chat" className={({ isActive }) => (isActive ? 'active' : '')}>
          Chat
        </NavLink>
        <NavLink to="/knowledge-gap" className={({ isActive }) => (isActive ? 'active' : '')}>
          Knowledge Gap
        </NavLink>
      </nav>

      <div className="main-area">{children}</div>
    </div>
  );
}
