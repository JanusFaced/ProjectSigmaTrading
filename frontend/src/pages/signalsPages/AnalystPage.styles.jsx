// AnalystPage.styles.jsx
import styled from 'styled-components';

// Контейнер всей страницы
export const CardsPage = styled.div`
    min-height: 100vh;
    padding: 48px 32px;
    background:
        radial-gradient(
            circle at top left,
            rgba(45, 212, 191, 0.07),
            transparent 34%
        ),
        #0b1120;
    color: #e5e7eb;

    h1 {
        max-width: 1400px;
        margin: 0 auto 42px;
        color: #f8fafc;
        font-size: clamp(30px, 4vw, 44px);
        font-weight: 700;
        letter-spacing: -0.04em;
        text-align: center;
    }

    @media (max-width: 768px) {
        padding: 32px 16px;

        h1 {
            margin-bottom: 28px;
        }
    }
`;

// Секция загрузки, ошибки и пустого состояния
export const LoadSection = styled.div`
    width: 100%;
    max-width: 520px;
    margin: 0 auto;
    padding: 48px 36px;
    border: 1px solid #263247;
    border-radius: 16px;
    background: #111827;
    box-shadow:
        0 20px 45px rgba(0, 0, 0, 0.25),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
    text-align: center;

    p {
        margin: 0 0 24px;
        color: #9ca3af;
        font-size: 16px;
        line-height: 1.6;
    }

    button {
        min-width: 130px;
        padding: 12px 22px;
        border: 1px solid #2dd4bf;
        border-radius: 8px;
        background: #134e4a;
        color: #ccfbf1;
        font-size: 15px;
        font-weight: 600;
        cursor: pointer;
        transition:
            background 0.2s ease,
            border-color 0.2s ease,
            transform 0.2s ease,
            box-shadow 0.2s ease;

        &:hover {
            border-color: #5eead4;
            background: #115e59;
            box-shadow: 0 0 0 4px rgba(45, 212, 191, 0.1);
            transform: translateY(-1px);
        }

        &:active {
            transform: translateY(0);
        }

        &:focus-visible {
            outline: 2px solid #5eead4;
            outline-offset: 3px;
        }
    }

    @media (max-width: 480px) {
        padding: 36px 22px;
    }
`;

// Спиннер загрузки
export const Spinner = styled.div`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 42px;
    height: 42px;
    margin-top: 4px;
    border: 3px solid #263247;
    border-top-color: #2dd4bf;
    border-radius: 50%;
    color: transparent;
    animation: spin 0.8s linear infinite;

    @keyframes spin {
        to {
            transform: rotate(360deg);
        }
    }
`;

// Сетка списка карточек
export const CardsList = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(340px, 1fr));
    gap: 24px;
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;

    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        gap: 18px;
    }

    @media (max-width: 400px) {
        grid-template-columns: minmax(0, 1fr);
    }
`;
