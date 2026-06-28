import styled from 'styled-components';

// Контейнер всей страницы
export const CardsPage = styled.div`
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px 20px;
    
    h1 {
        text-align: center;
        color: white;
        font-size: 42px;
        margin-bottom: 40px;
        font-weight: bold;
        
        @media (max-width: 768px) {
            font-size: 32px;
        }
    }
`;

// Секция загрузки/ошибки/пустого состояния
export const LoadSection = styled.div`
    text-align: center;
    background: white;
    border-radius: 16px;
    padding: 60px 40px;
    max-width: 500px;
    margin: 0 auto;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    
    p {
        font-size: 18px;
        color: #666;
        margin-bottom: 20px;
    }
    
    button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 16px;
        cursor: pointer;
        transition: transform 0.3s ease;
        
        &:hover {
            transform: translateY(-2px);
        }
    }
`;

// Спиннер загрузки
export const Spinner = styled.div`
    display: inline-block;
    font-size: 48px;
    animation: spin 1s linear infinite;
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;

// Сетка списка карточек
export const CardsList = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 30px;
    max-width: 1400px;
    margin: 0 auto;
    
    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        gap: 20px;
    }
`;