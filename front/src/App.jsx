import { useState } from 'react';
import './App.css';

function App() {
  const [login, setLogin] = useState('');
  const [password, setPassword] = useState('');
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const requestBody = {
      login,
      password,
    };

    try {
      const response = await fetch('/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody),
      });

      const data = await response.json();
      if (data.token) {
        setResult({ success: true, message: 'Успешно!' });
      } else {
        setResult({ success: false, message: 'Неверный логин или пароль!' });
        console.error(data.error);
      }
    } catch (error) {
      console.error('Error during fetch:', error);
      setResult({ success: false, message: `Произошла какая то ошибка. ${error.message}` });
    }
  };

  return (
    <div className="App">
      <h1>Authentication Form</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label>
            Login:
            <input
              type="text"
              value={login}
              onChange={(e) => setLogin(e.target.value)}
              required
            />
          </label>
        </div>
        <div>
          <label>
            Password:
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </label>
        </div>
        <button type="submit">Submit</button>
      </form>
      {result && (
        <div className={`result ${result.success ? 'success' : 'error'}`}>
          {result.message}
        </div>
      )}
    </div>
  );
}

export default App;
