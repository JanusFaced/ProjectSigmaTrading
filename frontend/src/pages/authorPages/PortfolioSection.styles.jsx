import styled from 'styled-components';

// Основная секция портфолио
export const PortfolioSectionMain = styled.section`
    padding: 80px 20px;
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    position: relative;
    
    @media (max-width: 768px) {
        padding: 60px 20px;
    }
`;

// Контейнер
export const Container = styled.div`
    max-width: 1200px;
    margin: 0 auto;
    
    h2 {
        text-align: center;
        font-size: 2.5rem;
        color: #1e3c72;
        margin-bottom: 3rem;
        position: relative;
        
        &::after {
            content: '';
            position: absolute;
            bottom: -10px;
            left: 50%;
            transform: translateX(-50%);
            width: 60px;
            height: 3px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            border-radius: 2px;
        }
        
        @media (max-width: 768px) {
            font-size: 2rem;
            margin-bottom: 2rem;
        }
    }
`;

// Сетка портфолио
export const PortfolioGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
    
    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
`;

// Карточка проекта — теперь кликабельная
export const ProjectCard = styled.div`
    background: white;
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    position: relative;
    
    &:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 30px rgba(0, 0, 0, 0.15);
    }
    
    &:active {
        transform: scale(0.98);
    }
`;

// Изображение проекта — теперь с логотипом
export const ProjectImage = styled.div`
    height: 200px;
    background: #ffffff;
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
    box-shadow: inset 0 -4px 10px rgba(0, 0, 0, 0.03); // ← лёгкая тень внутри
    
    &::before {
        display: none;
    }
`;

// ✅ Новый компонент для логотипа
export const LogoImage = styled.img`
    max-width: 100%;
    max-height: 100%;
    object-fit: contain;
    filter: drop-shadow(0 4px 20px rgba(0, 0, 0, 0.2));
    transition: all 0.3s ease;
    
    ${ProjectCard}:hover & {
        transform: scale(1.05);
        filter: drop-shadow(0 8px 30px rgba(0, 0, 0, 0.3));
    }
`;

// Информация о проекте
export const ProjectInfo = styled.div`
    padding: 1.5rem;
    
    h3 {
        font-size: 1.5rem;
        margin-bottom: 0.5rem;
        color: #1e3c72;
        transition: color 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: space-between;
        
        ${ProjectCard}:hover & {
            color: #667eea;
        }
    }
    
    p {
        color: #666;
        line-height: 1.6;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
`;

// Технологический стек
export const TechStack = styled.div`
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-top: 1rem;
`;

export const TechBadge = styled.span`
    background: #f0f0f0;
    color: #667eea;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
    transition: all 0.3s ease;
    
    &:hover {
        background: #667eea;
        color: white;
        transform: scale(1.05);
    }
`;

// Подсказка о клике
export const ClickableCard = styled.span`
    font-size: 0.75rem;
    color: #999;
    display: block;
    margin-top: 12px;
    text-align: right;
    opacity: 0.7;
    transition: opacity 0.3s ease;
    
    ${ProjectCard}:hover & {
        opacity: 1;
        color: #667eea;
    }
`;