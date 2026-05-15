import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
    // Состояния (как переменные, которые обновляют интерфейс)
    const [count, setCount] = useState(0);
    const [users, setUsers] = useState([]);
    const [loading, setLoading] = useState(false);
    const [showUsers, setShowUsers] = useState(false);

    // Простой счетчик
    const increment = () => setCount(count + 1);
    const decrement = () => setCount(count - 1);
    const reset = () => setCount(0);

    // Загрузка пользователей с API
    const loadUsers = async () => {
        setLoading(true);
        try {
            const response = await fetch('https://jsonplaceholder.typicode.com/users');
            const data = await response.json();
            setUsers(data);
            setShowUsers(true);
        } catch (error) {
            console.error('Ошибка загрузки:', error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="app">
            <h1>🚀 Моё первое React приложение</h1>
            
            {/* Счетчик */}
            <div className="counter-section">
                <h2>Счетчик: {count}</h2>
                <div className="button-group">
                    <button onClick={decrement}>-1</button>
                    <button onClick={reset}>Сброс</button>
                    <button onClick={increment}>+1</button>
                </div>
            </div>

            {/* Пользователи */}
            <div className="users-section">
                <h2>📱 Пользователи</h2>
                <button onClick={loadUsers} disabled={loading}>
                    {loading ? 'Загрузка...' : 'Загрузить пользователей'}
                </button>

                {showUsers && !loading && (
                    <div className="users-list">
                        {users.map(user => (
                            <div key={user.id} className="user-card">
                                <h3>{user.name}</h3>
                                <p>📧 {user.email}</p>
                                <p>📞 {user.phone}</p>
                                <p>🏢 {user.company.name}</p>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Информация */}
            <div className="info">
                <p>React приложение работает! 🎉</p>
                <p>Нажмите на кнопки, чтобы увидеть магию React</p>
            </div>
        </div>
    );
}

export default App;