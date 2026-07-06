import { useState } from "react";
import { useLocation } from 'react-router-dom';
import {
    Navbar,
    NavContainer,
    NavLogo,
    NavBurger,
    NavLinks,
    StyledNavLink,
    Overlay
} from './Navigator.styles.jsx';

function Navigator() {
    const [isOpen, setIsOpen] = useState(false);

    const closeMenu = () => {
        setIsOpen(false);
    };

    const location = useLocation();
    const isHome = location.pathname === '/';

    return (
        <>
            <Navbar>
                <NavContainer>
                    <NavLogo>
                        <StyledNavLink to="/" className={!isHome ? 'back-link' : ''}>
                            {isHome ? (
                                '🚀 MyPortfolio'
                            ) : (
                                <>
                                    <span style={{ fontSize: '0.8rem' }}>←</span> Вернуться на главную
                                </>
                            )}
                        </StyledNavLink>
                    </NavLogo>

                    <NavBurger 
                        $isOpen={isOpen}
                        onClick={() => setIsOpen(!isOpen)}
                    >
                        <span></span>
                        <span></span>
                        <span></span>
                    </NavBurger>

                    <NavLinks $isOpen={isOpen}>
                        <StyledNavLink 
                            to="/" 
                            onClick={closeMenu}
                        >
                            Welcome
                        </StyledNavLink>
                        <StyledNavLink 
                            to="/author"
                            onClick={closeMenu}
                        >
                            Author
                        </StyledNavLink>
                        <StyledNavLink 
                            to="/skills"
                            onClick={closeMenu}
                        >
                            Skills
                        </StyledNavLink>
                        <StyledNavLink 
                            to="/portfolio"
                            onClick={closeMenu}
                        >
                            Portfolio
                        </StyledNavLink>
                        <StyledNavLink 
                            to="/contact"
                            onClick={closeMenu}
                        >
                            Contact
                        </StyledNavLink>
                    </NavLinks>
                </NavContainer>
            </Navbar>
            <Overlay $isOpen={isOpen} onClick={closeMenu} />
        </>
    );
}

export default Navigator;