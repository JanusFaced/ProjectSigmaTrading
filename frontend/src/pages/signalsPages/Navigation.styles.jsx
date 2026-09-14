// Navigation.styles.jsx
import { Link } from 'react-router-dom';
import styled from 'styled-components';

// Основная навигационная панель
export const Nav = styled.nav`
    position: sticky;
    top: 0;
    z-index: 1000;
    border-bottom: 1px solid #263247;
    background: rgba(11, 17, 32, 0.92);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.22);
    backdrop-filter: blur(14px);
`;

// Внутренний контейнер
export const NavContainer = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 24px;
    max-width: 1440px;
    min-height: 76px;
    margin: 0 auto;
    padding: 12px 32px;

    @media (max-width: 1100px) {
        align-items: flex-start;
        flex-direction: column;
        gap: 12px;
        padding: 14px 24px;
    }

    @media (max-width: 600px) {
        padding: 12px 16px;
    }
`;

// Логотип
export const Logo = styled.div`
    display: flex;
    align-items: center;
    flex-shrink: 0;

    a {
        display: flex;
        align-items: center;
        gap: 11px;
        text-decoration: none;
        transition: opacity 0.2s ease;

        &:hover {
            opacity: 0.82;
        }

        &:focus-visible {
            outline: 2px solid #2dd4bf;
            outline-offset: 5px;
            border-radius: 5px;
        }
    }

    @media (max-width: 600px) {
        a {
            gap: 8px;
        }
    }
`;

// Изображения логотипа
export const LogoImage = styled.img`
    display: block;
    object-fit: contain;

    &.logo-icon {
        width: auto;
        height: 43px;
    }

    &.logo-name {
        width: auto;
        height: 31px;
    }

    @media (max-width: 600px) {
        &.logo-icon {
            height: 34px;
        }

        &.logo-name {
            height: 25px;
        }
    }
`;

// Список ссылок
export const NavLinks = styled.ul`
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: 6px 24px;
    max-width: 100%;
    margin: 0;
    padding: 0;
    list-style: none;
    flex-wrap: wrap;

    @media (max-width: 1100px) {
        width: 100%;
        justify-content: flex-start;
        gap: 4px 20px;
    }

    @media (max-width: 600px) {
        gap: 3px 14px;
    }
`;

// Элемент списка
export const NavItem = styled.li`
    margin: 0;

    button {
        padding: 8px 0 !important;
        color: #f87171 !important;
        font-family: inherit;
        font-size: 14px !important;
        font-weight: 600 !important;
        line-height: 1.4;
        transition:
            color 0.2s ease,
            opacity 0.2s ease;

        &:hover {
            color: #fca5a5 !important;
            opacity: 1;
        }

        &:focus-visible {
            outline: 2px solid #2dd4bf;
            outline-offset: 4px;
            border-radius: 3px;
        }
    }

    @media (max-width: 600px) {
        button {
            font-size: 13px !important;
        }
    }
`;

// Ссылка навигации
export const NavLink = styled(Link)`
    position: relative;
    display: inline-block;
    padding: 8px 0;
    color: #aeb8c8;
    font-size: 14px;
    font-weight: 600;
    line-height: 1.4;
    text-decoration: none;
    white-space: nowrap;
    transition:
        color 0.2s ease,
        opacity 0.2s ease;

    &::after {
        position: absolute;
        right: 0;
        bottom: 1px;
        left: 0;
        width: 0;
        height: 2px;
        border-radius: 2px;
        background: #2dd4bf;
        content: '';
        transition: width 0.2s ease;
    }

    &:hover {
        color: #f0fdfa;
    }

    &:hover::after {
        width: 100%;
    }

    &:focus-visible {
        outline: 2px solid #2dd4bf;
        outline-offset: 4px;
        border-radius: 3px;
    }

    @media (max-width: 600px) {
        font-size: 13px;
    }
`;

// Активная ссылка
export const ActiveNavLink = styled(NavLink)`
    color: #5eead4;

    &::after {
        width: 100%;
    }
`;
