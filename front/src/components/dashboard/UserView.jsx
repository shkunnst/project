import React from 'react';
import './AdminView.css'; // Reusing the same CSS for consistent styling

const UserView = ({ workData, departmentWorkData }) => {
  if (!workData) {
    return null;
  }

  return (
    <div>
      {/* Personal Work Information */}
      <div className="department-work-data">
        <div className="department-header">
          <h3>Ваша рабочая информация</h3>
        </div>
        
        <table className="department-table">
          <thead>
            <tr>
              <th>Рабочие часы</th>
              <th>Бонусы</th>
              <th>Штрафы</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{workData.working_hours}</td>
              <td>{workData.bonuses}</td>
              <td>{workData.fines}</td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Department Work Information (View Only) */}
      {departmentWorkData && departmentWorkData.length > 0 && (
        <div className="department-work-data">
          <div className="department-header">
            <h3>Информация о работе отдела</h3>
          </div>
          
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
        </div>
      )}
    </div>
  );
};

export default UserView;