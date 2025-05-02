import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

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
      sessionStorage.setItem('registrationSuccess', 'User registered successfully! Please login.');
      
      // Navigate to login page
      navigate('/login');
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