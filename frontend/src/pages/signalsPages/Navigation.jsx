import { 
    Nav, 
    NavContainer, 
    Logo, 
    LogoImage,
    NavLinks, 
    NavItem, 
    NavLink 
} from './Navigation.styles.jsx';

function Navigation() {
    const pstLogo = '/images/pst_logo_cut.png';
    const pstName = '/images/pst_name_cut.png';
    
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
                </NavLinks>
            </NavContainer>
        </Nav>
    );
}

export default Navigation;