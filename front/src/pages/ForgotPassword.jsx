import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authService } from '../services/auth';

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
      setHint(response.recovery_hint || 'Hint not available');
      setStep(2);
    } catch (err) {
      setError('Failed to get recovery hint. Please check your username.');
      console.error('Error getting hint:', err);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      await authService.recoverPassword(username, recoveryWord, newPassword);
      navigate('/login', { state: { message: 'Password reset successful! Please login with your new password.' } });
    } catch (err) {
      setError('Password reset failed. Please check your recovery word.');
      console.error('Password reset error:', err);
    }
  };

  return (
    <div className="forgot-password-container">
      <h2>Password Recovery</h2>
      {error && <div className="error-message">{error}</div>}
      
      {step === 1 && (
        <form onSubmit={handleGetHint}>
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />
          </div>
          <button type="submit">Get Recovery Hint</button>
        </form>
      )}
      
      {step === 2 && (
        <>
          <div className="hint-container">
            <p><strong>Recovery Hint:</strong> {hint}</p>
          </div>
          <form onSubmit={handleResetPassword}>
            <div className="form-group">
              <label htmlFor="recoveryWord">Recovery Word</label>
              <input
                type="text"
                id="recoveryWord"
                value={recoveryWord}
                onChange={(e) => setRecoveryWord(e.target.value)}
                required
              />
            </div>
            <div className="form-group">
              <label htmlFor="newPassword">New Password</label>
              <input
                type="password"
                id="newPassword"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
              />
            </div>
            <button type="submit">Reset Password</button>
          </form>
        </>
      )}
      
      <div className="links">
        <Link to="/login">Back to Login</Link>
      </div>
    </div>
  );
};

export default ForgotPassword;