import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [workData, setWorkData] = useState(null);
  const [departmentWorkData, setDepartmentWorkData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [departmentError, setDepartmentError] = useState('');

  useEffect(() => {
    const fetchUserWorkData = async () => {
      try {
        if (user && user.id) {
          console.log('Fetching user work data for ID:', user.id);
          const userWorkResponse = await api.get(`/api/work-data/${user.id}`);
          console.log('User work data response:', userWorkResponse.data);
          setWorkData(userWorkResponse.data);
        }
      } catch (err) {
        console.error('Error fetching user work data:', err);
        setError('Failed to load user work data');
      }
    };

    const fetchDepartmentWorkData = async () => {
      try {
        console.log('Attempting to fetch department work data');
        const departmentWorkResponse = await api.get('/api/department/work-data');
        console.log('Department work data response:', departmentWorkResponse.data);
        
        const workDataList = departmentWorkResponse.data || [];
        setDepartmentWorkData(workDataList);
      } catch (err) {
        console.error('Error fetching department work data:', err.response || err);
        setDepartmentError('Failed to load department work data');
      }
    };


    const loadData = async () => {
      if (user) {
        console.log('User data available, fetching work data');
        await fetchUserWorkData();
        await fetchDepartmentWorkData();
      } else {
        console.log('No user data available yet');
      }
      setLoading(false);
    };

    loadData();
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
          <div className="user-details">
            {user.role && <p><strong>Role:</strong> {user.role}</p>}
            {user.department && <p><strong>Department:</strong> {user.department}</p>}
          </div>
        </div>
      )}

      {workData && (
        <div className="work-data">
          <h3>Your Work Information</h3>
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

      {departmentError && <div className="error-message">{departmentError}</div>}
      
      {departmentWorkData.length > 0 ? (
        <div className="department-work-data">
          <h3>Department Work Information</h3>
          <table className="department-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Working Hours</th>
                <th>Bonuses</th>
                <th>Fines</th>
              </tr>
            </thead>
            <tbody>
              {departmentWorkData.map((item) => (
                <tr key={item.user_id}>
                  <td>{item.username}</td>
                  <td>{item.working_hours}</td>
                  <td>{item.bonuses}</td>
                  <td>{item.fines}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="department-work-data">
          <h3>Department Work Information</h3>
          <p>No department work data available</p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;