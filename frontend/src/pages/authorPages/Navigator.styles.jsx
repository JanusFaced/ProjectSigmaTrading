// Navigator.styles.js
import styled from 'styled-components';
import { NavLink } from 'react-router-dom';

// Основная навигационная панель
export const Navbar = styled.nav`
    position: sticky;
    top: 0;
    z-index: 1000;

    background: rgba(11, 15, 20, 0.92);
    border-bottom: 1px solid rgba(255, 255, 255, 0.08);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.28);

    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
`;

// Внутренний контейнер
export const NavContainer = styled.div`
    max-width: 1200px;
    min-height: 76px;
    margin: 0 auto;
    padding: 0 2rem;

    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
    position: relative;

    @media (max-width: 768px) {
        min-height: 68px;
        padding: 0 1.25rem;
    }
`;

// Логотип
export const NavLogo = styled.div`
    position: relative;
    z-index: 2;

    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    white-space: nowrap;

    a {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;

        color: #f1f5f9;
        text-decoration: none;

        transition:
            color 0.25s ease,
            transform 0.25s ease;

        &:hover {
            color: #8ab4f8;
            transform: translateY(-1px);
        }

        &:focus-visible {
            outline: 2px solid #8ab4f8;
            outline-offset: 5px;
            border-radius: 4px;
        }
    }

    .back-link {
        font-size: 1rem;
        color: #aab4c3;

        &:hover {
            color: #8ab4f8;
        }
    }

    @media (max-width: 768px) {
        font-size: 1.25rem;

        .back-link {
            font-size: 0.9rem;
        }
    }
`;

// Кнопка мобильного меню
export const NavBurger = styled.div`
    display: none;

    @media (max-width: 768px) {
        position: relative;
        z-index: 1002;

        display: flex;
        width: 30px;
        height: 24px;
        flex-direction: column;
        justify-content: space-between;

        cursor: pointer;
    }

    span {
        display: block;
        width: 100%;
        height: 2px;

        background: #d7dee8;
        border-radius: 999px;

        transition:
            transform 0.3s ease,
            opacity 0.25s ease,
            background 0.25s ease;
    }

    &:hover span {
        background: #8ab4f8;
    }

    ${({ $isOpen }) =>
        $isOpen &&
        `
        span:nth-child(1) {
            transform: translateY(11px) rotate(45deg);
        }

        span:nth-child(2) {
            opacity: 0;
        }

        span:nth-child(3) {
            transform: translateY(-11px) rotate(-45deg);
        }
    `}
`;

// Контейнер ссылок
export const NavLinks = styled.div`
    display: flex;
    align-items: center;
    gap: 0.35rem;

    @media (max-width: 768px) {
        position: fixed;
        top: 0;
        left: ${({ $isOpen }) => ($isOpen ? '0' : '-100%')};
        z-index: 1001;

        width: min(330px, 86vw);
        height: 100vh;
        padding: 6rem 2rem 2rem;

        display: flex;
        flex-direction: column;
        align-items: stretch;
        justify-content: flex-start;
        gap: 0.5rem;

        background: #111820;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        box-shadow: 16px 0 40px rgba(0, 0, 0, 0.35);

        transition: left 0.3s ease;
    }
`;

// Стилизованная ссылка
export const StyledNavLink = styled(NavLink)`
    position: relative;

    padding: 0.65rem 0.85rem;

    color: #aab4c3;
    font-size: 0.95rem;
    font-weight: 500;
    letter-spacing: 0.01em;
    text-decoration: none;

    border-radius: 7px;
    transition:
        color 0.25s ease,
        background 0.25s ease;

    &:hover {
        color: #f1f5f9;
        background: rgba(138, 180, 248, 0.08);
    }

    &:focus-visible {
        outline: 2px solid #8ab4f8;
        outline-offset: 2px;
    }

    &::after {
        content: '';

        position: absolute;
        left: 0.85rem;
        right: 0.85rem;
        bottom: 0.35rem;

        width: auto;
        height: 2px;

        background: #8ab4f8;
        border-radius: 999px;

        transform: scaleX(0);
        transform-origin: center;
        transition: transform 0.25s ease;
    }

    &:hover::after,
    &.active::after {
        transform: scaleX(1);
    }

    &.active {
        color: #f1f5f9;
        background: rgba(138, 180, 248, 0.1);
    }

    @media (max-width: 768px) {
        padding: 0.9rem 1rem;

        font-size: 1.15rem;
        border-radius: 8px;

        &::after {
            left: 1rem;
            right: auto;
            bottom: 0.65rem;
            width: 28px;
            transform-origin: left;
        }
    }
`;

// Затемнение фона на мобильных устройствах
export const Overlay = styled.div`
    display: none;

    @media (max-width: 768px) {
        position: fixed;
        inset: 0;
        z-index: 999;

        display: ${({ $isOpen }) => ($isOpen ? 'block' : 'none')};

        background: rgba(2, 6, 11, 0.68);
        backdrop-filter: blur(3px);
        -webkit-backdrop-filter: blur(3px);
    }
`;
