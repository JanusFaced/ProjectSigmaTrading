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
                    <NavLink to="/">[ PREDICT ]</NavLink>
                </Logo>
                <NavLinks>
                    <NavItem>
                        <NavLink to="/predict/">Главная</NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink to="/predict/analyst">Предсказания</NavLink>
                    </NavItem>
                    <NavItem>
                        <NavLink to="/predict/about">О проекте</NavLink>
                    </NavItem>
                </NavLinks>
            </NavContainer>
        </Nav>
    );
}

export default Navigation;