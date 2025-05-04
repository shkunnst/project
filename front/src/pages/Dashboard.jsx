import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../services/api';
import { adminService } from '../services/admin';
import './Dashboard.css';

// Import components
import UserInfo from '../components/dashboard/UserInfo';
import UserView from '../components/dashboard/UserView';
import ManagerView from '../components/dashboard/ManagerView';
import AdminView from '../components/dashboard/AdminView';

const Dashboard = () => {
  const { user, logout } = useAuth();
  const [workData, setWorkData] = useState(null);
  const [departmentWorkData, setDepartmentWorkData] = useState([]);
  const [allUsersWorkData, setAllUsersWorkData] = useState([]);
  const [departments, setDepartments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

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

        // Fetch department data for both managers and regular users
        if (user.role === 'руководитель' || user.role === 'подчиненный') {
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

  if (loading) return <div className="loading-container">Loading...</div>;

  const isManager = user && user.role === 'руководитель';
  const isAdmin = user && user.role === 'администратор';
  const isRegularUser = user && user.role === 'подчиненный';

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <div className="dashboard-actions">
          <button onClick={handleLogout} className="logout-button">Logout</button>
        </div>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* User Information Component */}
      <UserInfo user={user} workData={workData} />

      {/* User View Component for regular users */}
      {isRegularUser && <UserView 
        workData={workData} 
        departmentWorkData={departmentWorkData} 
      />}

      {/* Manager View Component */}
      {isManager && <ManagerView
        departmentWorkData={departmentWorkData}
        setDepartmentWorkData={setDepartmentWorkData}
      />}

      {/* Admin View Component */}
      {isAdmin && <AdminView
        allUsersWorkData={allUsersWorkData}
        setAllUsersWorkData={setAllUsersWorkData}
        departments={departments}
      />}
    </div>
  );
};

export default Dashboard;