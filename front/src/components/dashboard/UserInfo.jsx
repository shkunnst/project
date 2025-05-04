import React from 'react';
import './UserInfo.css';

const UserInfo = ({ user, workData }) => {
  return (
    <>
      <div className="user-info">
        <h2>Welcome, {user.username}</h2>
        <div className="user-details">
          {user.role && <p><strong>Role:</strong> {user.role}</p>}
          {user.department_name && <p><strong>Department:</strong> {user.department_name}</p>}
        </div>
      </div>

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
    </>
  );
};

export default UserInfo;