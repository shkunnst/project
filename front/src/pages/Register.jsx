import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import './Auth.css';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    recovery_word: '',
    recovery_hint: '',
    role: 'user' // Default role
  });
  const [error, setError] = useState('');
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    // Set a default department_id value (1) when submitting
    const submitData = {
      ...formData,
      department_id: 1
    };
    
    try {
      const response = await register(submitData);
      console.log('Registration successful:', response);
      
      // Store success message in sessionStorage to persist through redirect
      sessionStorage.setItem('registrationSuccess', '\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f \u0443\u0441\u043f\u0435\u0448\u043d\u043e \u0437\u0430\u043a\u043e\u043d\u0447\u0438\u0442\u0430\u043d\u0430! \u041f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u0432\u043e\u0439\u0434\u0438\u0442\u0435 \u0432 \u0441\u0438\u0441\u0442\u0435\u043c\u0443.');
      
      // Navigate to login page
      navigate('/login');
    } catch (err) {
      setError('\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f \u043d\u0435 \u0443\u0434\u0430\u043b\u0430\u0441\u044c. \u041f\u043e\u0436\u0430\u043b\u0443\u0439\u0441\u0442\u0430, \u043f\u043e\u043f\u0440\u043e\u0431\u0443\u0439\u0442\u0435 \u0435\u0449\u0435.');
      console.error('Registration error:', err);
    }
  };

  return (
    <div className="register-container">
      <h2>\u0420\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">\u0418\u043c\u044f \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u044f</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">\u041f\u0430\u0440\u043e\u043b\u044c</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="recovery_word">\u0421\u0435\u043a\u0440\u0435\u0442\u043d\u043e\u0435 \u0441\u043b\u043e\u0432\u043e</label>
          <input
            type="text"
            id="recovery_word"
            name="recovery_word"
            value={formData.recovery_word}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="recovery_hint">\u041f\u043e\u0434\u0441\u043a\u0430\u0437\u043a\u0430 \u0434\u043b\u044f \u0432\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u043b\u0435\u043d\u0438\u044f</label>
          <input
            type="text"
            id="recovery_hint"
            name="recovery_hint"
            value={formData.recovery_hint}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">\u0417\u0430\u0440\u0435\u0433\u0438\u0441\u0442\u0440\u0430\u0446\u0438\u044f\u0442\u044c\u0441\u044f</button>
      </form>
      <div className="links">
        <Link to="/login">\u0423\u0436\u0435 \u0435\u0441\u0442\u044c \u0430\u043a\u043a\u0430\u0443\u043d\u0442? \u0412\u043e\u0439\u0442\u0438</Link>
      </div>
    </div>
  );
};

export default Register;