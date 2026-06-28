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