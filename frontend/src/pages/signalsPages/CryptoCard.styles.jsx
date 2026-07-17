// CryptoCard.styles.js
import styled from 'styled-components';

// Карточка криптовалюты - более компактная
export const CryptoCardContainer = styled.div`
    background: white;
    border-radius: 12px;
    padding: 16px 20px 20px 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    transition: all 0.3s ease;
    min-width: 280px;
    max-width: 100%;
    
    &:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }
`;

// Заголовок карточки - более компактный
export const CardTitle = styled.h3`
    font-size: ${props => props.long ? '10px' : '18px'};
    color: #333;
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid #f0f0f0;
    text-align: center;
    font-weight: 700;
    letter-spacing: 0.3px;
    word-break: break-word;
    line-height: 1.4;
`;

// Таблица с данными - плотная верстка
export const CryptoTable = styled.table`
    width: 100%;
    border-collapse: collapse;
    font-size: 13px;
    
    td {
        padding: 6px 4px;
        vertical-align: middle;
    }
`;

// Ячейка с label - компактная
export const Label = styled.td`
    font-weight: 600;
    color: #888;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    padding: 4px 4px 2px 4px;
    white-space: nowrap;
`;

// Ячейка со значением
export const Value = styled.td`
    color: #333;
    font-weight: 500;
    font-size: 13px;
    padding: 4px 4px 2px 4px;
    white-space: nowrap;
`;

// Ячейка с сигналом - компактная
export const Signal = styled.td`
    font-weight: 700;
    font-size: 14px;
    padding: 4px 4px 2px 4px;
    white-space: nowrap;
    
    ${props => {
        // Long сигналы
        if (props.$signalType === 'long') {
            switch(props.$signalState) {
                case 'open':
                    return `
                        color: #10b981;
                        text-shadow: 0 0 5px rgba(16, 185, 129, 0.2);
                    `;
                case 'close':
                    return `
                        color: #ef4444;
                        text-shadow: 0 0 5px rgba(239, 68, 68, 0.2);
                    `;
                default:
                    return `
                        color: #6b7280;
                    `;
            }
        }
        
        // Short сигналы
        if (props.$signalType === 'short') {
            switch(props.$signalState) {
                case 'open':
                    return `
                        color: #3b82f6;
                        text-shadow: 0 0 5px rgba(59, 130, 246, 0.2);
                    `;
                case 'close':
                    return `
                        color: #8b5cf6;
                        text-shadow: 0 0 5px rgba(139, 92, 246, 0.2);
                    `;
                default:
                    return `
                        color: #6b7280;
                    `;
            }
        }
        
        return `
            color: #6b7280;
        `;
    }}
`;

// Индикатор сигнала - поменьше
export const SignalIndicator = styled.span`
    display: inline-block;
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 5px;
    flex-shrink: 0;
    
    ${props => {
        if (props.$signalType === 'long') {
            switch(props.$signalState) {
                case 'open':
                    return `
                        background-color: #10b981;
                        box-shadow: 0 0 4px rgba(16, 185, 129, 0.5);
                    `;
                case 'close':
                    return `
                        background-color: #ef4444;
                        box-shadow: 0 0 4px rgba(239, 68, 68, 0.5);
                    `;
                default:
                    return `
                        background-color: #6b7280;
                        box-shadow: none;
                    `;
            }
        }
        
        if (props.$signalType === 'short') {
            switch(props.$signalState) {
                case 'open':
                    return `
                        background-color: #3b82f6;
                        box-shadow: 0 0 4px rgba(59, 130, 246, 0.5);
                    `;
                case 'close':
                    return `
                        background-color: #8b5cf6;
                        box-shadow: 0 0 4px rgba(139, 92, 246, 0.5);
                    `;
                default:
                    return `
                        background-color: #6b7280;
                        box-shadow: none;
                    `;
            }
        }
        
        return `
            background-color: #6b7280;
            box-shadow: none;
        `;
    }}
    
    animation: pulse 2s infinite;
    
    @keyframes pulse {
        0% { opacity: 0.6; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.15); }
        100% { opacity: 0.6; transform: scale(1); }
    }
`;

// Контейнер для сигнала (чтобы текст и индикатор были в строку)
export const SignalWrapper = styled.div`
    display: flex;
    align-items: center;
    gap: 4px;
`;

// Специализированные компоненты
export const LongSignal = styled(Signal)``;
export const ShortSignal = styled(Signal)``;
export const LongSignalIndicator = styled(SignalIndicator)``;
export const ShortSignalIndicator = styled(SignalIndicator)``;

export const ViewButton = styled.button`
    padding: 4px 12px;
    background: #8b5cf6;
    color: white;
    border: none;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
    transition: all 0.3s ease;
    white-space: nowrap;
    
    &:hover {
        background: #7c3aed;
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
    }
`;

export const ActionCell = styled.td`
    padding: 4px 4px 2px 4px;
    white-space: nowrap;
`;