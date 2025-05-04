import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useState } from 'react';
import { authService } from '../services/auth';
import './Auth.css';

const ForgotPassword = () => {
  const [step, setStep] = useState(1);
  const [username, setUsername] = useState('');
  const [recoveryWord, setRecoveryWord] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [hint, setHint] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleGetHint = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await authService.getRecoveryHint(username);
      setHint(response.recovery_hint || 'Подсказка недоступна');
      setStep(2);
    } catch (err) {
      setError('Не удалось получить подсказку для восстановления. Пожалуйста, проверьте имя пользователя.');
      console.error('Error getting hint:', err);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      await authService.recoverPassword(username, recoveryWord, newPassword);
      navigate('/login', { state: { message: 'Пароль успешно сброшен! Пожалуйста, войдите с новым паролем.' } });
    } catch (err) {
      setError('Сброс пароля не удался. Пожалуйста, проверьте секретное слово.');
      console.error('Password reset error:', err);
    }
  };

  return (
    <div className="forgot-password-container">
      <h2>Восстановление пароля</h2>
      {error && <div className="error-message">{error}</div>}
      
      {step === 1 && (
        <form onSubmit={handleGetHint}>
          <div className="form-group">
            <label htmlFor="username">Имя пользователя</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <button type="submit">Получить подсказку</button>
        </form>
      )}
      
      {step === 2 && (
        <>
          <div className="hint-container">
            <p><strong>Подсказка для восстановления:</strong> {hint}</p>
          </div>
          <form onSubmit={handleResetPassword}>
            <div className="form-group">
              <label htmlFor="recoveryWord">Секретное слово</label>
              <input
                type="text"
                id="recoveryWord"
                value={recoveryWord}
                onChange={(e) => setRecoveryWord(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="newPassword">Новый пароль</label>
              <input
                type="password"
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit">Сбросить пароль</button>
          </form>
        </>
      )}
      
      <div className="links">
        <Link to="/login">Вернуться к входу</Link>
      </div>
    </div>
  );
};

export default ForgotPassword;