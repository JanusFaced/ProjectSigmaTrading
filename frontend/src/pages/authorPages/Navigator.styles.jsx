// Navigation.styles.js
import styled from 'styled-components';
import { NavLink } from 'react-router-dom';

// Основной контейнер навигации
export const Navbar = styled.nav`
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
    box-shadow: 0 2px 20px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
`;

// Внутренний контейнер
export const NavContainer = styled.div`
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: relative;
    
    @media (max-width: 768px) {
        padding: 0.8rem 1.5rem;
    }
`;

// Логотип
export const NavLogo = styled.div`
    font-size: 1.8rem;
    font-weight: bold;
    
    a {
        text-decoration: none;
        color: white;
        transition: transform 0.3s ease;
        display: inline-block;
        
        &:hover {
            transform: scale(1.05);
        }
    }
    
    @media (max-width: 768px) {
        font-size: 1.5rem;
    }
`;

// Бургер-иконка
export const NavBurger = styled.div`
    display: none;
    cursor: pointer;
    
    @media (max-width: 768px) {
        display: block;
        width: 30px;
        height: 20px;
        position: relative;
        z-index: 2;
    }
    
    span {
        display: block;
        width: 100%;
        height: 3px;
        background: white;
        border-radius: 3px;
        transition: all 0.3s ease;
        position: absolute;
        
        &:nth-child(1) {
            top: 0;
        }
        
        &:nth-child(2) {
            top: 50%;
            transform: translateY(-50%);
        }
        
        &:nth-child(3) {
            bottom: 0;
        }
    }
    
    // Анимация при активном состоянии
    ${props => props.$isOpen && `
        span:nth-child(1) {
            transform: rotate(45deg);
            top: 50%;
        }
        
        span:nth-child(2) {
            opacity: 0;
        }
        
        span:nth-child(3) {
            transform: rotate(-45deg);
            bottom: 50%;
        }
    `}
`;

// Контейнер ссылок
export const NavLinks = styled.div`
    display: flex;
    gap: 2rem;
    align-items: center;
    
    @media (max-width: 768px) {
        position: fixed;
        top: 0;
        left: ${props => props.$isOpen ? '0' : '-100%'};
        width: 100%;
        height: 100vh;
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        flex-direction: column;
        justify-content: center;
        gap: 2rem;
        transition: left 0.3s ease;
        z-index: 1;
    }
`;

// Стилизованная ссылка
export const StyledNavLink = styled(NavLink)`
    color: white;
    text-decoration: none;
    font-size: 1.1rem;
    font-weight: 500;
    padding: 0.5rem 0;
    position: relative;
    transition: all 0.3s ease;
    
    &:hover {
        color: #ffd700;
    }
    
    // Анимированное подчеркивание
    &::after {
        content: '';
        position: absolute;
        bottom: -2px;
        left: 0;
        width: 0;
        height: 2px;
        background: #ffd700;
        transition: width 0.3s ease;
    }
    
    &:hover::after {
        width: 100%;
    }
    
    // Активная ссылка
    &.active {
        color: #ffd700;
        
        &::after {
            width: 100%;
        }
    }
    
    @media (max-width: 768px) {
        font-size: 1.5rem;
    }
`;

// Оверлей для мобильного меню (опционально)
export const Overlay = styled.div`
    display: none;
    
    @media (max-width: 768px) {
        display: ${props => props.$isOpen ? 'block' : 'none'};
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 0;
    }
`;