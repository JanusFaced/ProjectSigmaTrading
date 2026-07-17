import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from './AuthContext.jsx';
import {
    LoadingContainer,
    LoadingContent,
    Spinner,
    LoadingText
} from './ProtectedRoute.styles.jsx';

const ProtectedRoute = ({ children }) => {
    const { isAuthenticated, loading } = useAuth();
    
    if (loading) {
        return (
            <LoadingContainer>
                <LoadingContent>
                    <Spinner />
                    <LoadingText>Проверка доступа...</LoadingText>
                </LoadingContent>
            </LoadingContainer>
        );
    }
    
    if (!isAuthenticated) {
        return <Navigate to="/signals/login" replace />;
    }
    
    return children;
};

export default ProtectedRoute;