import React, { useState } from 'react';
import { adminService } from '../../services/admin';
import './AdminView.css';

const AdminView = ({ allUsersWorkData, setAllUsersWorkData, departments }) => {
  const [adminEditMode, setAdminEditMode] = useState(false);
  const [editingUser, setEditingUser] = useState(null);

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

  return (
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
                <td>
                  {item.department_id 
                    ? departments.find(dept => dept.id === item.department_id)?.name || 'Unknown Department'
                    : 'No Department'}
                </td>
                <td>{item.working_hours}</td>
                <td>{item.bonuses}</td>
                <td>{item.fines}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
};

export default AdminView;