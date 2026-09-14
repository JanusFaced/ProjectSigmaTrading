import styled from 'styled-components';

// Основная секция портфолио
export const PortfolioSectionMain = styled.section`
    position: relative;
    overflow: hidden;
    padding: 100px 20px;

    background:
        radial-gradient(
            circle at 15% 25%,
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

// Сетка портфолио
export const PortfolioGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 1.5rem;
    max-width: 850px;
    margin: 0 auto;

    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        gap: 1.25rem;
    }
`;

// Карточка проекта
export const ProjectCard = styled.div`
    position: relative;
    overflow: hidden;
    border: 1px solid rgba(148, 163, 184, 0.14);
    border-radius: 16px;
    background: rgba(15, 23, 42, 0.7);
    box-shadow: 0 12px 35px rgba(0, 0, 0, 0.18);
    cursor: pointer;
    transition:
        transform 0.3s ease,
        border-color 0.3s ease,
        background 0.3s ease,
        box-shadow 0.3s ease;

    &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(
            90deg,
            transparent,
            #3b82f6,
            #8b5cf6,
            transparent
        );
        opacity: 0;
        transition: opacity 0.3s ease;
    }

    &:hover {
        border-color: rgba(96, 165, 250, 0.45);
        background: rgba(30, 41, 59, 0.82);
        box-shadow: 0 20px 45px rgba(0, 0, 0, 0.3);
        transform: translateY(-8px);
    }

    &:hover::after {
        opacity: 1;
    }

    &:active {
        transform: translateY(-3px) scale(0.99);
    }
`;

// Область с логотипом
export const ProjectImage = styled.div`
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    height: 220px;
    padding: 2rem;
    overflow: hidden;
    background:
        radial-gradient(
            circle at center,
            rgba(59, 130, 246, 0.14),
            transparent 55%
        ),
        #111827;
    border-bottom: 1px solid rgba(148, 163, 184, 0.12);

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
        background-size: 32px 32px;
        mask-image: radial-gradient(
            circle,
            black,
            transparent 75%
        );
        pointer-events: none;
    }

    @media (max-width: 768px) {
        height: 190px;
    }
`;

// Логотип проекта
export const LogoImage = styled.img`
    position: relative;
    z-index: 1;
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    filter: drop-shadow(0 8px 22px rgba(0, 0, 0, 0.35));
    transition:
        transform 0.35s ease,
        filter 0.35s ease;

    ${ProjectCard}:hover & {
        filter: drop-shadow(0 12px 30px rgba(59, 130, 246, 0.22));
        transform: scale(1.05);
    }
`;

// Информация о проекте
export const ProjectInfo = styled.div`
    padding: 1.6rem;

    h3 {
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 1rem;
        margin: 0 0 0.75rem;
        color: #e2e8f0;
        font-size: 1.45rem;
        font-weight: 650;
        line-height: 1.3;
        transition: color 0.25s ease;

        ${ProjectCard}:hover & {
            color: #60a5fa;
        }
    }

    p {
        margin: 0;
        color: #94a3b8;
        font-size: 0.98rem;
        line-height: 1.65;
    }
`;

// Технологический стек
export const TechStack = styled.div`
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1.25rem;
`;

export const TechBadge = styled.span`
    padding: 0.35rem 0.7rem;
    border: 1px solid rgba(96, 165, 250, 0.2);
    border-radius: 6px;
    background: rgba(30, 41, 59, 0.8);
    color: #93c5fd;
    font-size: 0.75rem;
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

// Подсказка о клике
export const ClickableCard = styled.span`
    display: block;
    margin-top: 1.1rem;
    color: #64748b;
    font-size: 0.78rem;
    line-height: 1.4;
    text-align: right;
    opacity: 0.8;
    transition:
        color 0.25s ease,
        opacity 0.25s ease;

    ${ProjectCard}:hover & {
        color: #60a5fa;
        opacity: 1;
    }

    h3 & {
        display: inline;
        margin: 0;
        font-size: 1rem;
        line-height: 1;
    }
`;
