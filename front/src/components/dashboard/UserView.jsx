import React from 'react';
import './AdminView.css'; // Reusing the same CSS for consistent styling

const UserView = ({ workData }) => {
  if (!workData) {
    console.error('No work data provided');
    return null;
  }

  return (
    <div className="department-work-data">
      <div className="department-header">
        <h3>Your Work Information</h3>
      </div>
      
      <table className="department-table">
        <thead>
          <tr>
            <th>Working Hours</th>
            <th>Bonuses</th>
            <th>Fines</th>
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
  );
};

export default UserView;