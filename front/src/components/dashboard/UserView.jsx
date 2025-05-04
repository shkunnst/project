import React from 'react';
import './AdminView.css'; // Reusing the same CSS for consistent styling

const UserView = ({ workData, departmentWorkData }) => {
  if (!workData) {
    return null;
  }

  return (
    <div>
      {/* Department Work Information (View Only) */}
      {departmentWorkData && departmentWorkData.length > 0 && (
        <div className="department-work-data">
          <div className="department-header">
            <h3>Department Work Information</h3>
          </div>
          
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
      )}
    </div>
  );
};

export default UserView;