// CryptoCard.styles.js
import styled from 'styled-components';

// Карточка криптовалюты
export const CryptoCardContainer = styled.div`
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
    
    &:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
    }
`;

// Заголовок карточки
export const CardTitle = styled.h3`
    font-size: 24px;
    color: #333;
    margin-bottom: 20px;
    padding-bottom: 12px;
    border-bottom: 2px solid #f0f0f0;
    text-align: center;
    font-weight: bold;
`;

// Таблица с данными
export const CryptoTable = styled.table`
    width: 100%;
    border-collapse: collapse;
    
    td {
        padding: 12px 8px;
        vertical-align: middle;
    }
`;

// Ячейка с label
export const Label = styled.td`
    font-weight: 600;
    color: #666;
    width: 35%;
    font-size: 14px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
`;

// Ячейка со значением (для ML модели и таймфрейма)
export const Value = styled.td`
    color: #333;
    font-weight: 500;
    font-size: 16px;
`;

// Ячейка с сигналом (цвет зависит от значения)
export const Signal = styled.td`
    font-weight: 700;
    font-size: 18px;
    
    // Динамические цвета для разных сигналов
    ${props => {
        switch(props.$signalType) {
            case 'buy':
                return `
                    color: #10b981;
                    text-shadow: 0 0 5px rgba(16, 185, 129, 0.3);
                `;
            case 'sell':
                return `
                    color: #ef4444;
                    text-shadow: 0 0 5px rgba(239, 68, 68, 0.3);
                `;
            case 'hold':
                return `
                    color: #f59e0b;
                    text-shadow: 0 0 5px rgba(245, 158, 11, 0.3);
                `;
            default:
                return `
                    color: #6b7280;
                `;
        }
    }}
`;

// Бонус: добавим индикатор сигнала
export const SignalIndicator = styled.span`
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 8px;
    background-color: ${props => {
        switch(props.$signalType) {
            case 'buy': return '#10b981';
            case 'sell': return '#ef4444';
            case 'hold': return '#f59e0b';
            default: return '#6b7280';
        }
    }};
    box-shadow: 0 0 5px ${props => {
        switch(props.$signalType) {
            case 'buy': return 'rgba(16, 185, 129, 0.5)';
            case 'sell': return 'rgba(239, 68, 68, 0.5)';
            case 'hold': return 'rgba(245, 158, 11, 0.5)';
            default: return 'none';
        }
    }};
    animation: pulse 2s infinite;
    
    @keyframes pulse {
        0% { opacity: 0.5; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.2); }
        100% { opacity: 0.5; transform: scale(1); }
    }
`;