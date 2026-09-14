// src/pages/signalsPages/TradesPage.styles.jsx
import styled from 'styled-components';

const borderColor = '#263247';
const cardBackground = '#111827';
const pageBackground = '#0b1120';
const mutedText = '#9ca3af';
const accent = '#2dd4bf';

// Основной контейнер страницы
export const PageContainer = styled.div`
    box-sizing: border-box;
    width: 100%;
    max-width: 1400px;
    min-height: 100vh;
    margin: 0 auto;
    padding: 32px;
    background:
        radial-gradient(
            circle at top left,
            rgba(45, 212, 191, 0.06),
            transparent 32%
        ),
        ${pageBackground};
    color: #e5e7eb;

    @media (max-width: 768px) {
        padding: 24px 16px;
    }

    @media (max-width: 480px) {
        padding: 18px 12px;
    }
`;

// Верхняя панель
export const Header = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    margin-bottom: 24px;
    padding: 20px 24px;
    border: 1px solid ${borderColor};
    border-radius: 14px;
    background: ${cardBackground};
    box-shadow:
        0 16px 35px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);

    h2 {
        margin: 0;
        color: #f8fafc;
        font-size: clamp(18px, 2.5vw, 25px);
        font-weight: 700;
        line-height: 1.35;
        letter-spacing: -0.02em;
    }

    @media (max-width: 768px) {
        flex-direction: column;
        align-items: stretch;
        padding: 18px;

        h2 {
            text-align: center;
        }
    }
`;

// Кнопка возврата
export const BackButton = styled.button`
    flex-shrink: 0;
    padding: 9px 16px;
    border: 1px solid #37445a;
    border-radius: 8px;
    background: #1f2937;
    color: #d1d5db;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        color 0.2s ease,
        transform 0.2s ease;

    &:hover {
        border-color: #4b617d;
        background: #273449;
        color: #f9fafb;
        transform: translateY(-1px);
    }

    &:active {
        transform: translateY(0);
    }

    &:focus-visible {
        outline: 2px solid ${accent};
        outline-offset: 3px;
    }

    @media (max-width: 768px) {
        width: 100%;
    }
`;

// Сетка статистики
export const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(155px, 1fr));
    gap: 16px;
    margin-bottom: 24px;

    @media (max-width: 480px) {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }
`;

// Карточка отдельного показателя
export const StatCard = styled.div`
    min-width: 0;
    padding: 17px 14px;
    border: 1px solid ${borderColor};
    border-radius: 12px;
    background: ${cardBackground};
    box-shadow:
        0 12px 26px rgba(0, 0, 0, 0.16),
        inset 0 1px 0 rgba(255, 255, 255, 0.02);
    text-align: center;

    label {
        display: block;
        margin-bottom: 7px;
        overflow: hidden;
        color: ${mutedText};
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-overflow: ellipsis;
        text-transform: uppercase;
        white-space: nowrap;
    }

    value {
        display: block;
        overflow: hidden;
        color: #f3f4f6;
        font-size: 21px;
        font-weight: 700;
        line-height: 1.2;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    @media (max-width: 480px) {
        padding: 13px 8px;

        value {
            font-size: 17px;
        }

        label {
            font-size: 9px;
        }
    }
`;

// Общая карточка графика и таблицы
export const ChartCard = styled.div`
    margin-bottom: 24px;
    padding: 24px;
    border: 1px solid ${borderColor};
    border-radius: 14px;
    background: ${cardBackground};
    box-shadow:
        0 16px 35px rgba(0, 0, 0, 0.2),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);

    h3 {
        margin: 0;
        color: #f3f4f6;
        font-size: 18px;
        font-weight: 650;
        line-height: 1.4;
    }

    @media (max-width: 768px) {
        padding: 18px;
    }

    @media (max-width: 480px) {
        padding: 15px;
    }
`;

// Панель управления графиком
export const ControlsContainer = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    margin-bottom: 22px;
    flex-wrap: wrap;

    @media (max-width: 600px) {
        align-items: stretch;
        flex-direction: column;
    }
`;

export const LimitGroup = styled.div`
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;

    span {
        margin-right: 4px;
        color: ${mutedText};
        font-size: 13px;
        font-weight: 500;
    }

    @media (max-width: 600px) {
        justify-content: flex-start;
    }
`;

export const LimitButton = styled.button`
    min-width: 42px;
    padding: 6px 10px;
    border: 1px solid
        ${props => (props.active ? accent : '#344158')};
    border-radius: 6px;
    background: ${props =>
        props.active ? 'rgba(19, 78, 74, 0.85)' : '#172033'};
    color: ${props => (props.active ? '#ccfbf1' : '#aeb8c8')};
    font-size: 12px;
    font-weight: ${props => (props.active ? '700' : '500')};
    cursor: pointer;
    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        color 0.2s ease,
        transform 0.2s ease;

    &:hover:not(:disabled) {
        border-color: ${accent};
        background: ${props =>
            props.active ? '#115e59' : '#203047'};
        color: #f0fdfa;
        transform: translateY(-1px);
    }

    &:active:not(:disabled) {
        transform: translateY(0);
    }

    &:disabled {
        cursor: not-allowed;
        opacity: 0.45;
    }

    &:focus-visible {
        outline: 2px solid ${accent};
        outline-offset: 2px;
    }

    @media (max-width: 480px) {
        min-width: 36px;
        padding: 5px 8px;
        font-size: 11px;
    }
`;

// Состояние загрузки
export const LoadingContainer = styled.div`
    display: flex;
    min-height: 420px;
    align-items: center;
    justify-content: center;
    color: #cbd5e1;
    font-size: 17px;
    font-weight: 500;
`;

// Состояние ошибки
export const ErrorContainer = styled.div`
    display: flex;
    min-height: 420px;
    align-items: center;
    justify-content: center;
    padding: 24px;
    color: #fca5a5;
    font-size: 17px;
    text-align: center;

    button {
        transition:
            background 0.2s ease,
            transform 0.2s ease;

        &:hover {
            background: #115e59 !important;
            transform: translateY(-1px);
        }

        &:focus-visible {
            outline: 2px solid ${accent};
            outline-offset: 3px;
        }
    }
`;

// Таблица сделок
export const TradesTable = styled.div`
    width: 100%;
    margin-top: 18px;
    overflow-x: auto;
    border: 1px solid ${borderColor};
    border-radius: 9px;

    table {
        width: 100%;
        min-width: 500px;
        border-collapse: collapse;
        color: #d1d5db;
        font-size: 13px;
    }

    thead {
        background: #172033;
    }

    th {
        padding: 13px 14px;
        border-bottom: 1px solid #344158;
        color: #9ca3af;
        font-size: 10px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-align: left;
        text-transform: uppercase;
        white-space: nowrap;
    }

    td {
        padding: 12px 14px;
        border-bottom: 1px solid #202c3f;
        color: #d1d5db;
        white-space: nowrap;
    }

    tbody tr:last-child td {
        border-bottom: none;
    }

    tbody tr {
        transition: background 0.2s ease;
    }

    tbody tr:hover {
        background: rgba(45, 212, 191, 0.035);
    }

    @media (max-width: 480px) {
        table {
            min-width: 430px;
            font-size: 12px;
        }

        th,
        td {
            padding: 10px;
        }
    }
`;

// Область графика
export const ChartContainer = styled.div`
    position: relative;
    height: 400px;
    padding-top: 8px;

    @media (max-width: 768px) {
        height: 320px;
    }

    @media (max-width: 480px) {
        height: 260px;
    }
`;

// Пагинация
export const PaginationContainer = styled.div`
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin-top: 20px;
    padding-top: 17px;
    border-top: 1px solid ${borderColor};
    flex-wrap: wrap;

    span {
        color: ${mutedText} !important;
    }

    @media (max-width: 600px) {
        gap: 5px;

        span {
            width: 100%;
            margin: 5px 0 0 !important;
            text-align: center;
        }
    }
`;

export const PageButton = styled.button`
    min-width: 36px;
    padding: 7px 10px;
    border: 1px solid
        ${props => (props.active ? accent : '#344158')};
    border-radius: 6px;
    background: ${props =>
        props.active ? 'rgba(19, 78, 74, 0.85)' : '#172033'};
    color: ${props => (props.active ? '#ccfbf1' : '#aeb8c8')};
    font-size: 13px;
    font-weight: ${props => (props.active ? '700' : '500')};
    cursor: pointer;
    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        color 0.2s ease,
        transform 0.2s ease;

    &:hover:not(:disabled) {
        border-color: ${accent};
        background: ${props =>
            props.active ? '#115e59' : '#203047'};
        color: #f0fdfa;
        transform: translateY(-1px);
    }

    &:active:not(:disabled) {
        transform: translateY(0);
    }

    &:disabled {
        cursor: not-allowed;
        opacity: 0.4;
    }

    &:focus-visible {
        outline: 2px solid ${accent};
        outline-offset: 2px;
    }

    @media (max-width: 480px) {
        min-width: 30px;
        padding: 5px 7px;
        font-size: 11px;
    }
`;
