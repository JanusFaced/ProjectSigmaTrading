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
                setError('❌ Invalid API key. Please try again.');
            } else {
                setError('❌ Error connecting to the server. Check your connection.');
            }
            setLoading(false);
        }
    };

    return (
        <LoginContainer>
            <LoginCard>
                <LoginTitle>🔐 Admin panel</LoginTitle>
                <LoginSubtitle>Enter the API key to access strategy management</LoginSubtitle>
                
                {error && <ErrorMessage>{error}</ErrorMessage>}
                
                <form onSubmit={handleSubmit}>
                    <FormGroup>
                        <Label>API Key</Label>
                        <Input
                            type="password"
                            value={key}
                            onChange={(e) => setKey(e.target.value)}
                            placeholder="Enter your API key..."
                            disabled={loading}
                            autoFocus
                        />
                    </FormGroup>
                    
                    <Button type="submit" disabled={loading || !key.trim()}>
                        {loading ? 'Examination...' : '🔑 Log in'}
                    </Button>
                </form>
                
                <InfoText>
                    Staff entrance only!
                </InfoText>
            </LoginCard>
        </LoginContainer>
    );
};

export default Login;