import { 
    Nav, 
    NavContainer, 
    Logo, 
    NavLinks, 
    NavItem, 
    NavLink 
} from './Navigation.styles.jsx';

function Navigation() {
    return (
        <Nav>
            <NavContainer>
                <Logo>
                    <NavLink to="/">SigmaProjectTrading</NavLink>
                </Logo>
                <NavLinks>
                    <NavItem>
                        <NavLink to="/signals/">Главная</NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink to="/signals/analyst">Аналитика</NavLink>
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