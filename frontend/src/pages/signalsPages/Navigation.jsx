import React from 'react';
import { 
    Nav, 
    NavContainer, 
    Logo, 
    LogoImage,
    NavLinks, 
    NavItem, 
    NavLink 
} from './Navigation.styles.jsx';
import { useAuth } from './AuthContext.jsx';

function Navigation() {
    const pstLogo = '/images/pst_logo_cut_remove.png';
    const pstName = '/images/pst_name_cut_remove.png';
    const { isAuthenticated, logout } = useAuth();

    const handleLogout = () => {
        if (window.confirm('Вы уверены, что хотите выйти?')) {
            logout();
            window.location.href = '/signals/';
        }
    };

    return (
        <Nav>
            <NavContainer>
                <Logo>
                    <NavLink to="/signals/">
                        <LogoImage src={pstLogo} alt="PST Logo" className="logo-icon" />
                        <LogoImage src={pstName} alt="PST Name" className="logo-name" />
                    </NavLink>
                </Logo>
                <NavLinks>
                    <NavItem>
                        <NavLink to="/signals/">Главная</NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink to="/signals/backtest">Бэктесты стратегий</NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink to="/signals/analyst">Торговые роботы</NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink to="/signals/about">О проекте</NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink to="/signals/admin" style={{ 
                            color: isAuthenticated ? '#28a745' : '#667eea',
                            fontWeight: 'bold'
                        }}>
                            {isAuthenticated ? 'Панель Администратора' : '🔑 Вход'}
                        </NavLink>
                    </NavItem>
                    {isAuthenticated && (
                        <NavItem>
                            <button
                                onClick={handleLogout}
                                style={{
                                    background: 'none',
                                    border: 'none',
                                    color: '#dc3545',
                                    fontWeight: '500',
                                    cursor: 'pointer',
                                    padding: '0.5rem 0',
                                    fontSize: '16px',
                                    transition: 'all 0.3s ease'
                                }}
                                onMouseEnter={(e) => e.target.style.color = '#c82333'}
                                onMouseLeave={(e) => e.target.style.color = '#dc3545'}
                            >
                                🚪 Выход
                            </button>
                        </NavItem>
                    )}
                </NavLinks>
            </NavContainer>
        </Nav>
    );
}

export default Navigation;