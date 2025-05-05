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
      sessionStorage.setItem('registrationSuccess', 'Регистрация успешно закончена! Пожалуйста, войдите в систему.');
      
      // Navigate to login page
      navigate('/login');
    } catch (err) {
      setError('Регистрация не удалась. Пожалуйста, попробуйте еще.');
      console.error('Registration error:', err);
    }
  };

  return (
    <div className="register-container">
      <h2>Регистрация</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Имя пользователя</label>
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
          <label htmlFor="password">Пароль</label>
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
          <label htmlFor="recovery_word">Секретное слово</label>
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
          <label htmlFor="recovery_hint">Подсказка для восстановления</label>
          <input
            type="text"
            id="recovery_hint"
            name="recovery_hint"
            value={formData.recovery_hint}
            onChange={handleChange}
            required
          />
        </div>
        <button type="submit">Зарегистрироваться</button>
      </form>
      <div className="links">
        <Link to="/login">Уже есть аккаунт? Войти</Link>
      </div>
    </div>
  );
};

export default Register;