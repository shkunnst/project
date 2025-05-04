import React from 'react';
import './UserInfo.css';

const UserInfo = ({ user, workData }) => {
  return (
    <>
      <div className="user-info">
        <h2>Добро пожаловать, {user.username}</h2>
        <div className="user-details">
          {user.role && <p><strong>Роль:</strong> {user.role}</p>}
          {user.department_name && <p><strong>Отдел:</strong> {user.department_name}</p>}
        </div>
      </div>

      {workData && (
        <div className="work-data">
          <h3>Ваша рабочая информация</h3>
          <div className="work-stats">
            <div className="stat-card">
              <h4>Рабочие часы</h4>
              <p>{workData.working_hours}</p>
            </div>
            <div className="stat-card">
              <h4>Бонусы</h4>
              <p>{workData.bonuses}</p>
            </div>
            <div className="stat-card">
              <h4>Штрафы</h4>
              <p>{workData.fines}</p>
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default UserInfo;