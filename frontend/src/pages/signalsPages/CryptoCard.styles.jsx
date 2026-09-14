// CryptoCard.styles.jsx
import styled from 'styled-components';

// Карточка с данными
export const CryptoCardContainer = styled.div`
    width: 100%;
    min-width: 280px;
    max-width: 100%;
    padding: 20px;
    border: 1px solid #263247;
    border-radius: 14px;
    background: #111827;
    box-shadow:
        0 16px 35px rgba(0, 0, 0, 0.22),
        inset 0 1px 0 rgba(255, 255, 255, 0.025);
    transition:
        transform 0.25s ease,
        border-color 0.25s ease,
        box-shadow 0.25s ease;

    &:hover {
        border-color: #34445d;
        box-shadow:
            0 20px 42px rgba(0, 0, 0, 0.3),
            0 0 0 1px rgba(45, 212, 191, 0.05);
        transform: translateY(-3px);
    }

    @media (max-width: 480px) {
        min-width: 0;
        padding: 16px;
    }
`;

// Заголовок карточки
export const CardTitle = styled.h3`
    min-height: ${props => (props.long ? '42px' : 'auto')};
    margin: 0 0 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #263247;
    color: #f3f4f6;
    font-size: ${props => (props.long ? '13px' : '18px')};
    font-weight: 700;
    line-height: 1.4;
    letter-spacing: ${props => (props.long ? '0.1px' : '-0.01em')};
    text-align: center;
    word-break: break-word;
`;

// Таблица с данными
export const CryptoTable = styled.table`
    width: 100%;
    border-collapse: collapse;
    color: #d1d5db;
    font-size: 13px;

    td {
        vertical-align: middle;
    }

    tr:nth-child(2),
    tr:nth-child(4),
    tr:nth-child(6) {
        border-bottom: 1px solid #202c3f;
    }

    tr:nth-child(2) td,
    tr:nth-child(4) td,
    tr:nth-child(6) td {
        padding-bottom: 12px;
    }

    tr:nth-child(3) td,
    tr:nth-child(5) td {
        padding-top: 12px;
    }
`;

// Названия полей
export const Label = styled.td`
    width: 33.333%;
    padding: 5px 4px 3px;
    color: #6b7280;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.08em;
    line-height: 1.3;
    text-transform: uppercase;
    white-space: nowrap;

    &:not(:first-child) {
        padding-left: 8px;
    }
`;

// Обычные значения
export const Value = styled.td`
    max-width: 150px;
    padding: 5px 4px 3px;
    overflow: hidden;
    color: #d1d5db;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.4;
    text-overflow: ellipsis;
    white-space: nowrap;

    &:not(:first-child) {
        padding-left: 8px;
    }
`;

// Общий стиль сигналов
export const Signal = styled.td`
    padding: 5px 4px 3px;
    font-size: 13px;
    font-weight: 700;
    line-height: 1.4;
    white-space: nowrap;

    ${props => {
        if (props.$signalType === 'long') {
            if (props.$signalState === 'open') {
                return `
                    color: #34d399;
                    text-shadow: 0 0 10px rgba(52, 211, 153, 0.2);
                `;
            }

            if (props.$signalState === 'close') {
                return `
                    color: #fb7185;
                    text-shadow: 0 0 10px rgba(251, 113, 133, 0.18);
                `;
            }
        }

        if (props.$signalType === 'short') {
            if (props.$signalState === 'open') {
                return `
                    color: #60a5fa;
                    text-shadow: 0 0 10px rgba(96, 165, 250, 0.2);
                `;
            }

            if (props.$signalState === 'close') {
                return `
                    color: #c084fc;
                    text-shadow: 0 0 10px rgba(192, 132, 252, 0.18);
                `;
            }
        }

        return `
            color: #9ca3af;
        `;
    }}
`;

// Индикатор сигнала
export const SignalIndicator = styled.span`
    display: inline-block;
    width: 7px;
    height: 7px;
    margin-right: 6px;
    border-radius: 50%;
    vertical-align: middle;
    flex-shrink: 0;

    ${props => {
        if (props.$signalType === 'long') {
            if (props.$signalState === 'open') {
                return `
                    background: #34d399;
                    box-shadow: 0 0 8px rgba(52, 211, 153, 0.7);
                `;
            }

            if (props.$signalState === 'close') {
                return `
                    background: #fb7185;
                    box-shadow: 0 0 8px rgba(251, 113, 133, 0.65);
                `;
            }
        }

        if (props.$signalType === 'short') {
            if (props.$signalState === 'open') {
                return `
                    background: #60a5fa;
                    box-shadow: 0 0 8px rgba(96, 165, 250, 0.7);
                `;
            }

            if (props.$signalState === 'close') {
                return `
                    background: #c084fc;
                    box-shadow: 0 0 8px rgba(192, 132, 252, 0.65);
                `;
            }
        }

        return `
            background: #6b7280;
            box-shadow: none;
        `;
    }}

    animation: pulse 2.2s ease-in-out infinite;

    @keyframes pulse {
        0%,
        100% {
            opacity: 0.65;
            transform: scale(0.9);
        }

        50% {
            opacity: 1;
            transform: scale(1.1);
        }
    }
`;

// Контейнер для сигнала
export const SignalWrapper = styled.div`
    display: inline-flex;
    align-items: center;
    gap: 4px;
`;

// Специализированные компоненты сигналов
export const LongSignal = styled(Signal)``;

export const ShortSignal = styled(Signal)``;

export const LongSignalIndicator = styled(SignalIndicator)``;

export const ShortSignalIndicator = styled(SignalIndicator)``;

// Кнопка открытия графика
export const ViewButton = styled.button`
    padding: 7px 11px;
    border: 1px solid #2dd4bf;
    border-radius: 7px;
    background: rgba(19, 78, 74, 0.75);
    color: #ccfbf1;
    font-size: 11px;
    font-weight: 700;
    line-height: 1;
    cursor: pointer;
    white-space: nowrap;
    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        transform 0.2s ease;

    &:hover {
        border-color: #5eead4;
        background: #115e59;
        box-shadow: 0 5px 16px rgba(45, 212, 191, 0.18);
        transform: translateY(-1px);
    }

    &:active {
        transform: translateY(0);
    }

    &:focus-visible {
        outline: 2px solid #5eead4;
        outline-offset: 3px;
    }

    @media (max-width: 480px) {
        padding: 7px 8px;
        font-size: 10px;
    }
`;

// Ячейка с действием
export const ActionCell = styled.td`
    padding: 5px 4px 3px;
    text-align: right;
    white-space: nowrap;
`;
