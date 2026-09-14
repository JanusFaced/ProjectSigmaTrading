// ContactSection.styles.js
import styled, { keyframes } from 'styled-components';

const rotate = keyframes`
    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }
`;

const fadeInDown = keyframes`
    from {
        opacity: 0;
        transform: translateY(-24px);
    }

    to {
        opacity: 1;
        transform: translateY(0);
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

// Основная секция контактов
export const ContactSectionMain = styled.section`
    position: relative;
    overflow: hidden;
    padding: 100px 20px;

    background:
        radial-gradient(
            circle at 15% 25%,
            rgba(59, 130, 246, 0.1),
            transparent 32%
        ),
        radial-gradient(
            circle at 85% 75%,
            rgba(139, 92, 246, 0.08),
            transparent 32%
        ),
        #0b0f19;

    &::before {
        content: '';
        position: absolute;
        top: -30%;
        right: -15%;
        width: 650px;
        height: 650px;
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
            rgba(0, 0, 0, 0.5),
            transparent 80%
        );
        pointer-events: none;
    }

    @media (prefers-reduced-motion: reduce) {
        &::before {
            animation: none;
        }
    }

    @media (max-width: 768px) {
        padding: 70px 20px;
    }
`;

// Контейнер
export const Container = styled.div`
    position: relative;
    z-index: 1;
    max-width: 800px;
    margin: 0 auto;
    text-align: center;

    h2 {
        margin: 0 0 1rem;
        color: #f8fafc;
        font-size: clamp(2rem, 4vw, 2.8rem);
        font-weight: 700;
        line-height: 1.15;
        letter-spacing: -0.03em;
        animation: ${fadeInDown} 0.8s ease both;
    }

    & > p {
        max-width: 600px;
        margin: 0 auto 2.5rem;
        color: #94a3b8;
        font-size: 1.1rem;
        line-height: 1.7;
        animation: ${fadeInUp} 0.8s ease both;

        @media (max-width: 768px) {
            font-size: 1rem;
        }
    }
`;

// Контейнер контактных ссылок
export const ContactLinks = styled.div`
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
    max-width: 500px;
    margin: 0 auto;
    animation: ${fadeInUp} 0.8s ease 0.2s both;
`;

// Элемент контакта
export const ContactItem = styled.a`
    display: flex;
    align-items: center;
    gap: 1rem;
    min-height: 64px;
    padding: 0.85rem 1rem 0.85rem 1.2rem;
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 12px;
    background: rgba(15, 23, 42, 0.68);
    backdrop-filter: blur(12px);
    color: #e2e8f0;
    font-size: 1rem;
    text-decoration: none;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.14);
    transition:
        background 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease,
        transform 0.25s ease;

    &:hover {
        border-color: rgba(96, 165, 250, 0.5);
        background: rgba(30, 41, 59, 0.8);
        box-shadow: 0 14px 35px rgba(0, 0, 0, 0.24);
        transform: translateX(6px);
    }

    &:focus-visible {
        outline: 3px solid rgba(96, 165, 250, 0.35);
        outline-offset: 3px;
    }

    @media (max-width: 768px) {
        min-height: 58px;
        padding: 0.75rem 0.8rem 0.75rem 1rem;
        font-size: 0.9rem;
    }
`;

// Иконка контакта
export const ContactIcon = styled.span`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 36px;
    width: 36px;
    height: 36px;
    border: 1px solid rgba(96, 165, 250, 0.2);
    border-radius: 9px;
    background: rgba(37, 99, 235, 0.12);
    font-size: 1.25rem;

    @media (max-width: 768px) {
        flex-basis: 32px;
        width: 32px;
        height: 32px;
        font-size: 1.1rem;
    }
`;

// Текст контакта
export const ContactText = styled.span`
    flex: 1;
    min-width: 0;
    overflow-wrap: anywhere;
    color: #cbd5e1;
    text-align: left;
`;

// Социальные сети
export const SocialGrid = styled.div`
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.85rem;
    margin-top: 2rem;
    animation: ${fadeInUp} 0.8s ease 0.4s both;

    @media (max-width: 480px) {
        flex-direction: column;
        align-items: stretch;
        max-width: 500px;
        margin-right: auto;
        margin-left: auto;
    }
`;

export const SocialLink = styled.a`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    min-width: 140px;
    padding: 0.75rem 1.1rem;
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 10px;
    background: rgba(15, 23, 42, 0.58);
    color: #94a3b8;
    font-size: 0.9rem;
    text-decoration: none;
    transition:
        background 0.25s ease,
        border-color 0.25s ease,
        color 0.25s ease,
        transform 0.25s ease;

    &:hover {
        border-color: rgba(96, 165, 250, 0.5);
        background: rgba(37, 99, 235, 0.15);
        color: #bfdbfe;
        transform: translateY(-3px);
    }

    &:focus-visible {
        outline: 3px solid rgba(96, 165, 250, 0.35);
        outline-offset: 3px;
    }
`;

// Кнопка копирования
export const CopyButton = styled.button`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    flex: 0 0 34px;
    width: 34px;
    height: 34px;
    margin-left: auto;
    border: 1px solid rgba(148, 163, 184, 0.2);
    border-radius: 7px;
    background: rgba(30, 41, 59, 0.8);
    color: #94a3b8;
    font-size: 0.85rem;
    cursor: pointer;
    transition:
        background 0.25s ease,
        border-color 0.25s ease,
        color 0.25s ease,
        transform 0.25s ease;

    &:hover {
        border-color: rgba(96, 165, 250, 0.6);
        background: rgba(37, 99, 235, 0.2);
        color: #dbeafe;
        transform: scale(1.05);
    }

    &:focus-visible {
        outline: 3px solid rgba(96, 165, 250, 0.35);
        outline-offset: 3px;
    }
`;
