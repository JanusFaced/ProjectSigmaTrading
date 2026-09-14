// WelcomeSection.styles.js
import styled, { keyframes } from 'styled-components';

const rotate = keyframes`
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
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

// Основной контейнер Welcome-секции
export const WelcomeHeader = styled.header`
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;

    background:
        radial-gradient(
            circle at 20% 20%,
            rgba(59, 130, 246, 0.12),
            transparent 35%
        ),
        radial-gradient(
            circle at 80% 75%,
            rgba(139, 92, 246, 0.1),
            transparent 35%
        ),
        #0b0f19;

    color: #f8fafc;

    &::before {
        content: '';
        position: absolute;
        top: -35%;
        right: -20%;
        width: 700px;
        height: 700px;
        border: 1px solid rgba(148, 163, 184, 0.08);
        border-radius: 50%;
        box-shadow:
            0 0 0 80px rgba(148, 163, 184, 0.025),
            0 0 0 160px rgba(148, 163, 184, 0.02);
        animation: ${rotate} 35s linear infinite;
        pointer-events: none;
    }

    &::after {
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
            rgba(0, 0, 0, 0.45),
            transparent 75%
        );
        pointer-events: none;
    }

    @media (prefers-reduced-motion: reduce) {
        &::before {
            animation: none;
        }
    }
`;

// Контейнер для контента
export const Container = styled.div`
    position: relative;
    z-index: 1;
    width: min(800px, 100%);
    margin: 0 auto;
    padding: 2rem;
    text-align: center;

    h1 {
        max-width: 760px;
        margin: 0 auto 1.5rem;
        color: #f8fafc;
        font-size: clamp(2.4rem, 6vw, 4.5rem);
        font-weight: 700;
        line-height: 1.08;
        letter-spacing: -0.04em;
        text-shadow: 0 10px 40px rgba(0, 0, 0, 0.35);
        animation: ${fadeInUp} 0.8s ease both;
    }
`;

// Тэглайн
export const Tagline = styled.p`
    max-width: 620px;
    margin: 0 auto;
    color: #94a3b8;
    font-size: clamp(1.05rem, 2vw, 1.35rem);
    line-height: 1.7;
    font-weight: 400;
    letter-spacing: 0.01em;
    animation: ${fadeInUp} 0.8s ease 0.15s both;
`;

// Декоративная кнопка
export const ScrollButton = styled.button`
    margin-top: 3rem;
    padding: 0.8rem 1.8rem;
    border: 1px solid rgba(96, 165, 250, 0.7);
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.65);
    color: #bfdbfe;
    font-size: 1rem;
    font-weight: 500;
    cursor: pointer;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.2);
    transition:
        background 0.25s ease,
        border-color 0.25s ease,
        color 0.25s ease,
        transform 0.25s ease,
        box-shadow 0.25s ease;
    animation: ${fadeInUp} 0.8s ease 0.3s both;

    &:hover {
        border-color: #60a5fa;
        background: rgba(37, 99, 235, 0.18);
        color: #eff6ff;
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(37, 99, 235, 0.2);
    }

    &:active {
        transform: translateY(-1px);
    }

    &:focus-visible {
        outline: 3px solid rgba(96, 165, 250, 0.4);
        outline-offset: 4px;
    }

    @media (max-width: 768px) {
        margin-top: 2.5rem;
        padding: 0.7rem 1.4rem;
        font-size: 0.95rem;
    }
`;
