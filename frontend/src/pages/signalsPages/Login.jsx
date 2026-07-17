import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';
import axios from 'axios';
import { 
    LoginContainer,
    LoginCard,
    LoginTitle,
    LoginSubtitle,
    FormGroup,
    Label,
    Input,
    Button,
    ErrorMessage,
    InfoText,
} from './Login.styles.jsx';

const API_BASE = process.env.REACT_APP_API_URL;

const Login = () => {
    const [key, setKey] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await axios.get(`${API_BASE}/admin/statistics`, {
                headers: {
                    'X-API-Key': key
                }
            });
            
            login(key);
            navigate(`/signals/admin`, { replace: true });
        } catch (err) {
            if (err.response?.status === 403) {
                setError('❌ Неверный API ключ. Попробуйте еще раз.');
            } else {
                setError('❌ Ошибка подключения к серверу. Проверьте соединение.');
            }
            setLoading(false);
        }
    };

    return (
        <LoginContainer>
            <LoginCard>
                <LoginTitle>🔐 Админ-панель</LoginTitle>
                <LoginSubtitle>Введите API ключ для доступа к управлению стратегиями</LoginSubtitle>
                
                {error && <ErrorMessage>{error}</ErrorMessage>}
                
                <form onSubmit={handleSubmit}>
                    <FormGroup>
                        <Label>API Ключ</Label>
                        <Input
                            type="password"
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                            placeholder="Введите ваш API ключ..."
                            disabled={loading}
                            autoFocus
                        />
                    </FormGroup>
                    
                    <Button type="submit" disabled={loading || !key.trim()}>
                        {loading ? 'Проверка...' : '🔑 Войти'}
                    </Button>
                </form>
                
                <InfoText>
                    Вход только для АДМИНИСТРАЦИИ!
                </InfoText>
            </LoginCard>
        </LoginContainer>
    );
};

export default Login;