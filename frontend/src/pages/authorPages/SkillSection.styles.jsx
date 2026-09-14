// SkillSection.styles.js
import styled, { keyframes } from 'styled-components';

const float = keyframes`
    0% {
        transform: translateY(0);
    }

    50% {
        transform: translateY(-6px);
    }

    100% {
        transform: translateY(0);
    }
`;

const fadeInUp = keyframes`
    from {
        opacity: 0;
        transform: translateY(20px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
    }
`;

// Основная секция навыков
export const ServicesSection = styled.section`
    position: relative;
    overflow: hidden;
    padding: 100px 20px;

    background:
        radial-gradient(
            circle at 15% 20%,
            rgba(59, 130, 246, 0.08),
            transparent 30%
        ),
        radial-gradient(
            circle at 85% 75%,
            rgba(139, 92, 246, 0.07),
            transparent 30%
        ),
        #0b0f19;

    @media (max-width: 768px) {
        padding: 70px 20px;
    }
`;

// Контейнер
export const Container = styled.div`
    position: relative;
    z-index: 1;
    max-width: 1200px;
    margin: 0 auto;

    h2 {
        position: relative;
        margin: 0 0 4rem;
        color: #f8fafc;
        text-align: center;
        font-size: clamp(2rem, 4vw, 2.8rem);
        font-weight: 700;
        letter-spacing: -0.03em;
        animation: ${fadeInUp} 0.7s ease both;

        &::after {
            content: '';
            position: absolute;
            right: 50%;
            bottom: -1.2rem;
            width: 64px;
            height: 3px;
            border-radius: 10px;
            background: linear-gradient(
                90deg,
                #3b82f6,
                #8b5cf6
            );
            transform: translateX(50%);
        }
    }
`;

// Сетка карточек
export const ServicesGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1.5rem;

    @media (max-width: 950px) {
        grid-template-columns: repeat(2, 1fr);
    }

    @media (max-width: 680px) {
        grid-template-columns: 1fr;
        gap: 1.25rem;
    }
`;

// Карточка услуги/навыка
export const ServiceCard = styled.article`
    min-height: 360px;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 2rem 1.6rem;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.65);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.16);
    text-align: center;
    cursor: default;
    transition:
        transform 0.3s ease,
        border-color 0.3s ease,
        background 0.3s ease,
        box-shadow 0.3s ease;
    animation: ${fadeInUp} 0.7s ease both;

    &:hover {
        border-color: rgba(96, 165, 250, 0.45);
        background: rgba(30, 41, 59, 0.78);
        box-shadow: 0 18px 45px rgba(0, 0, 0, 0.25);
        transform: translateY(-7px);
    }

    h3 {
        margin: 1rem 0;
        color: #e2e8f0;
        font-size: 1.35rem;
        font-weight: 650;
        line-height: 1.3;
        transition: color 0.25s ease;
    }

    p {
        margin: 0;
        color: #94a3b8;
        font-size: 0.98rem;
        line-height: 1.65;
    }

    &:hover h3 {
        color: #60a5fa;
    }
`;

// Иконка сервиса
export const ServiceIcon = styled.div`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 76px;
    height: 76px;
    border: 1px solid rgba(96, 165, 250, 0.18);
    border-radius: 18px;
    background: rgba(37, 99, 235, 0.1);
    font-size: 2.8rem;
    line-height: 1;
    animation: ${float} 3.5s ease-in-out infinite;
`;

// Стек технологий
export const TechStack = styled.div`
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
    margin-top: auto;
    padding-top: 1.5rem;
`;

export const TechBadge = styled.span`
    padding: 0.35rem 0.7rem;
    border: 1px solid rgba(96, 165, 250, 0.2);
    border-radius: 6px;
    background: rgba(30, 41, 59, 0.8);
    color: #93c5fd;
    font-size: 0.78rem;
    font-weight: 500;
    transition:
        background 0.25s ease,
        border-color 0.25s ease,
        color 0.25s ease,
        transform 0.25s ease;

    &:hover {
        border-color: rgba(96, 165, 250, 0.6);
        background: rgba(37, 99, 235, 0.2);
        color: #dbeafe;
        transform: translateY(-2px);
    }
`;

// Декоративный элемент
export const DecorativeLine = styled.div`
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
`;
