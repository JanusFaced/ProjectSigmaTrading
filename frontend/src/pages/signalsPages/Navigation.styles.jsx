import { Link } from 'react-router-dom';
import styled from 'styled-components';

// Основной контейнер навигации
export const Nav = styled.nav`
    background: rgba(255, 255, 255, 0.95);
    backdrop-filter: blur(10px);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    position: sticky;
    top: 0;
    z-index: 1000;
`;

// Внутренний контейнер с максимальной шириной
export const NavContainer = styled.div`
    max-width: 1200px;
    margin: 0 auto;
    padding: 1rem 2rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    
    @media (max-width: 768px) {
        padding: 1rem;
    }
`;

// Логотип
export const Logo = styled.div`
    font-size: 1.5rem;
    font-weight: bold;
    
    a {
        text-decoration: none;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-clip: text;
        -webkit-background-clip: text;
        color: transparent;
        transition: opacity 0.3s ease;
        
        &:hover {
            opacity: 0.8;
        }
    }
    
    @media (max-width: 768px) {
        font-size: 1.2rem;
    }
`;

// Список навигационных ссылок
export const NavLinks = styled.ul`
    display: flex;
    gap: 2rem;
    list-style: none;
    margin: 0;
    padding: 0;
    
    @media (max-width: 768px) {
        gap: 1rem;
    }
`;

// Элемент списка
export const NavItem = styled.li`
    margin: 0;
`;

// Стилизованная ссылка
export const NavLink = styled(Link)`
    text-decoration: none;
    color: #333;
    font-weight: 500;
    transition: all 0.3s ease;
    position: relative;
    padding: 0.5rem 0;
    
    &:hover {
        color: #667eea;
    }
    
    // Анимированное подчеркивание
    &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 0;
        height: 2px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        transition: width 0.3s ease;
    }
    
    &:hover::after {
        width: 100%;
    }
`;

// Активная ссылка (если нужно будет добавить активный класс)
export const ActiveNavLink = styled(NavLink)`
    color: #667eea;
    
    &::after {
        width: 100%;
    }
`;