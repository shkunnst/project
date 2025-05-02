import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [workData, setWorkData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const fetchWorkData = async () => {
      try {
        if (user && user.id) {
          const response = await api.get(`/api/work-data/${user.id}`);
          setWorkData(response.data);
        }
      } catch (err) {
        console.error('Error fetching work data:', err);
        setError('Failed to load work data');
      } finally {
        setLoading(false);
      }
    };

    fetchWorkData();
  }, [user]);

  const handleLogout = () => {
    logout();
  };

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <button onClick={handleLogout} className="logout-button">Logout</button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {user && (
        <div className="user-info">
          <h2>Welcome, {user.username}</h2>
          {user.department && <p>Department: {user.department}</p>}
        </div>
      )}

      {workData && (
        <div className="work-data">
          <h3>Work Information</h3>
          <div className="work-stats">
            <div className="stat-card">
              <h4>Working Hours</h4>
              <p>{workData.working_hours}</p>
            </div>
            <div className="stat-card">
              <h4>Bonuses</h4>
              <p>{workData.bonuses}</p>
            </div>
            <div className="stat-card">
              <h4>Fines</h4>
              <p>{workData.fines}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;