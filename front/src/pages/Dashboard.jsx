import React from 'react';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import api from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [workData, setWorkData] = useState(null);
  const [departmentWorkData, setDepartmentWorkData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [departmentError, setDepartmentError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);

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
        const departmentWorkResponse = await api.get('/api/department/work-data');

        const workDataList = departmentWorkResponse.data || [];
        setDepartmentWorkData(workDataList);
      } catch (err) {
        console.error('Error fetching department work data:', err.response || err);
        setDepartmentError('Failed to load department work data');
      }
    };

    const loadData = async () => {
      if (user) {
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

  const handleEditEmployee = (employee) => {
    setEditingEmployee(employee);
    setEditMode(true);
  };

  const handleSaveEmployeeData = async () => {
    try {
      await api.put(`/api/work-data/${editingEmployee.user_id}`, {
        working_hours: editingEmployee.working_hours,
        bonuses: editingEmployee.bonuses,
        fines: editingEmployee.fines
      });
      
      // Refresh department data
      const departmentWorkResponse = await api.get('/api/department/work-data');
      setDepartmentWorkData(departmentWorkResponse.data || []);
      
      setEditMode(false);
      setEditingEmployee(null);
    } catch (err) {
      console.error('Error updating employee data:', err);
      alert('Failed to update employee data');
    }
  };

  const handleCancelEdit = () => {
    setEditMode(false);
    setEditingEmployee(null);
  };

  const handleInputChange = (field, value) => {
    setEditingEmployee({
      ...editingEmployee,
      [field]: value
    });
  };

  if (loading) return <div>Loading...</div>;

  const isManager = user && user.role === 'руководитель';
  const isAdmin = user && user.role === 'администратор';

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="dashboard-actions">
          {isAdmin && (
            <Link to="/admin" className="admin-link">
              Admin Panel
            </Link>
          )}
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}
      {user && (
        <div className="user-info">
          <h2>Welcome, {user.username}</h2>
          <div className="user-details">
            {user.role && <p><strong>Role:</strong> {user.role}</p>}
            {user.department_name && <p><strong>Department:</strong> {user.department_name}</p>}
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
          <div className="department-header">
            <h3>Department Work Information</h3>
            {isManager && !editMode && (
              <button 
                className="edit-employees-button"
                onClick={() => setEditMode(true)}
              >
                Edit Employee Data
              </button>
            )}
          </div>
          
          {editMode ? (
            <div className="edit-employee-form">
              {editingEmployee ? (
                <>
                  <h4>Editing data for {editingEmployee.username}</h4>
                  <div className="edit-form-fields">
                    <div className="form-group">
                      <label>Working Hours</label>
                      <input 
                        type="number" 
                        value={editingEmployee.working_hours} 
                        onChange={(e) => handleInputChange('working_hours', e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <label>Bonuses</label>
                      <input 
                        type="number" 
                        value={editingEmployee.bonuses} 
                        onChange={(e) => handleInputChange('bonuses', e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <label>Fines</label>
                      <input 
                        type="number" 
                        value={editingEmployee.fines} 
                        onChange={(e) => handleInputChange('fines', e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="edit-actions">
                    <button onClick={handleSaveEmployeeData} className="save-button">Save</button>
                    <button onClick={handleCancelEdit} className="cancel-button">Cancel</button>
                  </div>
                </>
              ) : (
                <table className="department-table">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Working Hours</th>
                      <th>Bonuses</th>
                      <th>Fines</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {departmentWorkData.map((item) => (
                      <tr key={item.user_id}>
                        <td>{item.username}</td>
                        <td>{item.working_hours}</td>
                        <td>{item.bonuses}</td>
                        <td>{item.fines}</td>
                        <td>
                          <button 
                            onClick={() => handleEditEmployee(item)}
                            className="edit-button"
                          >
                            Edit
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              {!editingEmployee && (
                <button onClick={() => setEditMode(false)} className="cancel-button">
                  Cancel Editing
                </button>
              )}
            </div>
          ) : (
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
          )}
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