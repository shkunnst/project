import React, { useState } from 'react';
import api from '../../services/api';
import './AdminView.css'; // Reusing the same CSS for consistent styling

const ManagerView = ({ departmentWorkData, setDepartmentWorkData }) => {
  const [editMode, setEditMode] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState(null);

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
      alert('Не удалось обновить данные сотрудника');
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

  if (!departmentWorkData || departmentWorkData.length === 0) {
    return null;
  }

  return (
    <div className="department-work-data">
      <div className="department-header">
        <h3>Информация о работе отдела</h3>
        {!editMode && (
          <button 
            className="edit-employees-button"
            onClick={() => setEditMode(true)}
          >
            Редактировать данные сотрудников
          </button>
        )}
      </div>
      
      {editMode ? (
        <div className="edit-employee-form">
          {editingEmployee ? (
            <>
              <h4>Редактирование данных для {editingEmployee.username}</h4>
              <div className="edit-form-fields">
                <div className="form-group">
                  <label>Рабочие часы</label>
                  <input 
                    type="number" 
                    value={editingEmployee.working_hours} 
                    onChange={(e) => handleInputChange('working_hours', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Бонусы</label>
                  <input 
                    type="number" 
                    value={editingEmployee.bonuses} 
                    onChange={(e) => handleInputChange('bonuses', e.target.value)}
                  />
                </div>
                <div className="form-group">
                  <label>Штрафы</label>
                  <input 
                    type="number" 
                    value={editingEmployee.fines} 
                    onChange={(e) => handleInputChange('fines', e.target.value)}
                  />
                </div>
              </div>
              <div className="edit-actions">
                <button onClick={handleSaveEmployeeData} className="save-button">Сохранить</button>
                <button onClick={handleCancelEdit} className="cancel-button">Отмена</button>
              </div>
            </>
          ) : (
            <table className="department-table">
              <thead>
                <tr>
                  <th>Имя пользователя</th>
                  <th>Рабочие часы</th>
                  <th>Бонусы</th>
                  <th>Штрафы</th>
                  <th>Действия</th>
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
                        Редактировать
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
          {!editingEmployee && (
            <button onClick={() => setEditMode(false)} className="cancel-button">
              Отменить редактирование
            </button>
          )}
        </div>
      ) : (
        <table className="department-table">
          <thead>
            <tr>
              <th>Имя пользователя</th>
              <th>Рабочие часы</th>
              <th>Бонусы</th>
              <th>Штрафы</th>
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
  );
};

export default ManagerView;