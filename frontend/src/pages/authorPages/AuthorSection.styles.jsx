// AuthorSection.styles.js
import styled, { keyframes } from 'styled-components';
import { NavLink } from 'react-router-dom';

const slideInLeft = keyframes`
    from {
        opacity: 0;
        transform: translateX(-35px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
`;

const slideInRight = keyframes`
    from {
        opacity: 0;
        transform: translateX(35px);
    }

    to {
        opacity: 1;
        transform: translateX(0);
    }
`;

const fadeInUp = keyframes`
    from {
        opacity: 0;
        transform: translateY(24px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
`;

// Основная секция об авторе
export const HeroSection = styled.section`
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    padding: 100px 20px;

    background:
        radial-gradient(
            circle at 10% 20%,
            rgba(59, 130, 246, 0.1),
            transparent 32%
        ),
        radial-gradient(
            circle at 90% 80%,
            rgba(139, 92, 246, 0.08),
            transparent 32%
        ),
        #0b0f19;

    color: #f8fafc;

    &::before {
        content: '';
        position: absolute;
        inset: 0;
        background-image:
            linear-gradient(
                rgba(148, 163, 184, 0.035) 1px,
                transparent 1px
            ),
            linear-gradient(
                90deg,
                rgba(148, 163, 184, 0.035) 1px,
                transparent 1px
            );
        background-size: 48px 48px;
        mask-image: linear-gradient(
            to bottom,
            rgba(0, 0, 0, 0.5),
            transparent 80%
        );
        pointer-events: none;
    }

    &::after {
        content: '';
        position: absolute;
        right: 0;
        bottom: 0;
        left: 0;
        height: 1px;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(96, 165, 250, 0.65),
            transparent
        );
    }
`;

// Контейнер для контента
export const Container = styled.div`
    position: relative;
    z-index: 1;
    width: min(980px, 100%);
    margin: 0 auto;
    text-align: center;

    h1 {
        margin: 0 0 1rem;
        color: #f8fafc;
        font-size: clamp(2.8rem, 7vw, 5rem);
        font-weight: 750;
        line-height: 1.05;
        letter-spacing: -0.05em;
        text-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
        animation: ${slideInLeft} 0.8s ease both;
    }
`;

// Теглайн автора
export const AuthorTagline = styled.p`
    margin: 0 0 1.5rem;
    color: #60a5fa;
    font-size: clamp(1.2rem, 3vw, 1.8rem);
    font-weight: 600;
    line-height: 1.4;
    letter-spacing: 0.01em;
    animation: ${slideInRight} 0.8s ease both;
`;

// Описание
export const Description = styled.p`
    max-width: 650px;
    margin: 0 auto 2rem;
    color: #94a3b8;
    font-size: 1.15rem;
    line-height: 1.8;
    animation: ${fadeInUp} 0.8s ease 0.2s both;

    @media (max-width: 768px) {
        font-size: 1rem;
        line-height: 1.65;
    }
`;

// Основная кнопка
export const CTAButton = styled(NavLink)`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 150px;
    padding: 0.9rem 1.8rem;
    border: 1px solid rgba(96, 165, 250, 0.8);
    border-radius: 10px;
    background: #2563eb;
    color: #eff6ff;
    font-size: 1rem;
    font-weight: 600;
    text-decoration: none;
    box-shadow: 0 10px 30px rgba(37, 99, 235, 0.2);
    transition:
        background 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.25s ease;
    animation: ${fadeInUp} 0.8s ease 0.4s both;

    &:hover {
        border-color: #93c5fd;
        background: #3b82f6;
        box-shadow: 0 14px 35px rgba(37, 99, 235, 0.3);
        transform: translateY(-3px);
    }

    &:active {
        transform: translateY(-1px);
    }

    &:focus-visible {
        outline: 3px solid rgba(96, 165, 250, 0.4);
        outline-offset: 4px;
    }

    @media (max-width: 768px) {
        padding: 0.8rem 1.5rem;
        font-size: 0.95rem;
    }
`;

// Социальные ссылки
export const SocialLinks = styled.div`
    display: flex;
    justify-content: center;
    gap: 1.25rem;
    margin-top: 2rem;
    animation: ${fadeInUp} 0.8s ease 0.6s both;
`;

export const SocialIcon = styled.a`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.55);
    color: #94a3b8;
    font-size: 1.35rem;
    text-decoration: none;
    transition:
        background 0.25s ease,
        border-color 0.25s ease,
        color 0.25s ease,
        transform 0.25s ease;

    &:hover {
        border-color: rgba(96, 165, 250, 0.65);
        background: rgba(37, 99, 235, 0.15);
        color: #60a5fa;
        transform: translateY(-3px);
    }

    &:focus-visible {
        outline: 3px solid rgba(96, 165, 250, 0.35);
        outline-offset: 3px;
    }
`;

// Блок статистики
export const Stats = styled.div`
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-top: 4rem;
    animation: ${fadeInUp} 0.8s ease 0.6s both;

    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        max-width: 420px;
        margin: 3rem auto 0;
    }
`;

export const StatItem = styled.div`
    min-height: 145px;
    padding: 1.5rem 1.25rem;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 14px;
    background: rgba(15, 23, 42, 0.58);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.16);
    text-align: left;
    transition:
        border-color 0.25s ease,
        background 0.25s ease,
        transform 0.25s ease;

    &:hover {
        border-color: rgba(96, 165, 250, 0.4);
        background: rgba(30, 41, 59, 0.72);
        transform: translateY(-4px);
    }

    h3 {
        margin: 0 0 0.75rem;
        color: #e2e8f0;
        font-size: 1.05rem;
        font-weight: 650;
        line-height: 1.35;
    }

    p {
        margin: 0;
        color: #64748b;
        font-size: 0.9rem;
        line-height: 1.5;
    }

    @media (max-width: 768px) {
        min-height: auto;
        text-align: center;
    }
`;
