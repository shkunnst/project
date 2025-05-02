import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    department_id: '',
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
      [name]: name === 'department_id' ? parseInt(value, 10) : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      await register(formData);
      navigate('/login', { state: { message: 'Registration successful! Please login.' } });
    } catch (err) {
      setError('Registration failed. Please try again.');
      console.error('Registration error:', err);
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
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
          <label htmlFor="password">Password</label>
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
          <label htmlFor="department_id">Department ID</label>
          <input
            type="number"
            id="department_id"
            name="department_id"
            value={formData.department_id}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="recovery_word">Recovery Word</label>
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
          <label htmlFor="recovery_hint">Recovery Hint</label>
          <input
            type="text"
            id="recovery_hint"
            name="recovery_hint"
            value={formData.recovery_hint}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">Register</button>
      </form>
      <div className="links">
        <Link to="/login">Already have an account? Login</Link>
      </div>
    </div>
  );
};

export default Register;