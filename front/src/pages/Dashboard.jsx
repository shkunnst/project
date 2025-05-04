import React from 'react';
import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { Link } from 'react-router-dom';
import api from '../services/api';
import { adminService } from '../services/admin';
import './Dashboard.css';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [workData, setWorkData] = useState(null);
  const [departmentWorkData, setDepartmentWorkData] = useState([]);
  const [allUsersWorkData, setAllUsersWorkData] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [editMode, setEditMode] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);
  const [adminEditMode, setAdminEditMode] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

  useEffect(() => {
    const fetchUserWorkData = async () => {
      try {
        if (user && user.id) {
          const userWorkResponse = await api.get(`/api/work-data/${user.id}`);
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
      }
    };

    const fetchAllUsersWorkData = async () => {
      try {
        const allUsersData = await adminService.getAllUsersWorkData();
        setAllUsersWorkData(allUsersData || []);
      } catch (err) {
        console.error('Error fetching all users work data:', err);
      }
    };

    const fetchDepartments = async () => {
      try {
        const departmentsData = await adminService.getDepartments();
        setDepartments(departmentsData || []);
      } catch (err) {
        console.error('Error fetching departments:', err);
      }
    };

    const loadData = async () => {
      if (user) {
        await fetchUserWorkData();
        
        if (user.role === 'руководитель') {
          await fetchDepartmentWorkData();
        }
        
        if (user.role === 'администратор') {
          await fetchAllUsersWorkData();
          await fetchDepartments();
        }
      }
      setLoading(false);
    };

    loadData();
  }, [user]);

  const handleLogout = () => {
    logout();
  };

  // Manager functionality
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
      
      setEditingEmployee(null);
    } catch (err) {
      console.error('Error updating employee data:', err);
      alert('Failed to update employee data');
    }
  };

  const handleCancelEdit = () => {
    console.log("Canceling edit");
    setEditingEmployee(null);
  };

  const handleInputChange = (field, value) => {
    setEditingEmployee({
      ...editingEmployee,
      [field]: value
    });
  };

  // Admin functionality
  const handleAdminEditUser = (userData) => {
    setEditingUser(userData);
    setAdminEditMode(true);
  };

  const handleAdminSaveUser = async () => {
    try {
      await adminService.updateUserAdminData(editingUser.user_id, {
        username: editingUser.username,
        role: editingUser.role,
        department_id: editingUser.department_id,
        working_hours: editingUser.working_hours,
        bonuses: editingUser.bonuses,
        fines: editingUser.fines
      });

      // Refresh all users data
      const allUsersData = await adminService.getAllUsersWorkData();
      setAllUsersWorkData(allUsersData || []);

      setEditingUser(null);
    } catch (err) {
      console.error('Error updating user data:', err);
      alert('Failed to update user data');
    }
  };

  const handleAdminCancelEdit = () => {
    setEditingUser(null);
  };

  const handleAdminInputChange = (field, value) => {
    setEditingUser({
      ...editingUser,
      [field]: value
    });
  };

  if (loading) return <div className="loading-container">Loading...</div>;

  const isManager = user && user.role === 'руководитель';
  const isAdmin = user && user.role === 'администратор';

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="dashboard-actions">
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

      {/* Manager View - Department Work Data */}
      {isManager && departmentWorkData.length > 0 && (
        <div className="department-work-data">
          <div className="department-header">
            <h3>Department Work Information</h3>
            {!editMode && (
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
      )}

      {/* Admin View - All Users Work Data */}
      {isAdmin && (
        <div className="admin-section">
          <div className="admin-header">
            <h3>All Users Information</h3>
            {!adminEditMode && (
              <button 
                className="edit-users-button"
                onClick={() => setAdminEditMode(true)}
              >
                Edit User Data
              </button>
            )}
          </div>
          
          {adminEditMode ? (
            <div className="edit-user-form">
              {editingUser ? (
                <>
                  <h4>Editing data for {editingUser.username}</h4>
                  <div className="edit-form-fields">
                    <div className="form-group">
                      <label>Username</label>
                      <input 
                        type="text" 
                        value={editingUser.username} 
                        onChange={(e) => handleAdminInputChange('username', e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                    <div className="form-group">
                      <label>Role</label>
                      <select 
                        value={editingUser.role} 
                        onChange={(e) => handleAdminInputChange('role', e.target.value)}
                      >
                        <option value="подчиненный">Подчиненный</option>
                        <option value="руководитель">Руководитель</option>
                        <option value="администратор">Администратор</option>
                      </select>
                    </div>
                    </div>
                    <div className="form-group">
<div className="form-group">
  <label>Department</label>
  <select 
    value={editingUser.department_id || ''}
    onChange={(e) => handleAdminInputChange('department_id', e.target.value === '' ? null : e.target.value)}
  >
    <option value="">No Department</option>
    {departments.map((dept) => (
      <option key={dept.id} value={dept.id}>{dept.name}</option>
    ))}
  </select>
</div>
                    </div>
                    <div className="form-group">
                      <label>Working Hours</label>
                      <input 
                        type="number" 
                        value={editingUser.working_hours} 
                        onChange={(e) => handleAdminInputChange('working_hours', e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <label>Bonuses</label>
                      <input 
                        type="number" 
                        value={editingUser.bonuses} 
                        onChange={(e) => handleAdminInputChange('bonuses', e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <label>Fines</label>
                      <input 
                        type="number" 
                        value={editingUser.fines} 
                        onChange={(e) => handleAdminInputChange('fines', e.target.value)}
                      />
                    </div>
                  </div>
                  <div className="edit-actions">
                    <button onClick={handleAdminSaveUser} className="save-button">Save</button>
                    <button onClick={handleAdminCancelEdit} className="cancel-button">Cancel</button>
                  </div>
                </>
              ) : (
                <table className="admin-table">
                  <thead>
                    <tr>
                      <th>Username</th>
                      <th>Role</th>
                      <th>Department</th>
                      <th>Working Hours</th>
                      <th>Bonuses</th>
                      <th>Fines</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {allUsersWorkData.map((item) => (
                      <tr key={item.user_id}>
                        <td>{item.username}</td>
                        <td>{item.role}</td>
<td>
  {item.department_id 
    ? departments.find(dept => dept.id === item.department_id)?.name || 'Unknown Department'
    : 'No Department'}
</td>
                        <td>{departments.find(dept => dept.id === item.department_id)?.name || 'N/A'}</td>
                        <td>{item.working_hours}</td>
                        <td>{item.bonuses}</td>
                        <td>{item.fines}</td>
                        <td>
                          <button 
                            onClick={() => handleAdminEditUser(item)}
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
              {!editingUser && (
                <button onClick={() => setAdminEditMode(false)} className="cancel-button">
                  Cancel Editing
                </button>
              )}
            </div>
          ) : (
            <table className="admin-table">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Role</th>
                  <th>Department</th>
                  <th>Working Hours</th>
                  <th>Bonuses</th>
                  <th>Fines</th>
                </tr>
              </thead>
              <tbody>
                {allUsersWorkData.map((item) => (
                  <tr key={item.user_id}>
                    <td>{item.username}</td>
                    <td>{item.role}</td>
                    <td>{departments.find(dept => dept.id === item.department_id)?.name || 'N/A'}</td>
                    <td>{item.working_hours}</td>
                    <td>{item.bonuses}</td>
                    <td>{item.fines}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      )}
    </div>
  );
};

export default Dashboard;