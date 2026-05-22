// PortfolioSection.styles.jsx
import styled from 'styled-components';
import { Link } from 'react-router-dom'; // ← Добавить импорт Link

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

// Карточка проекта
export const ProjectCard = styled.div`
    background: white;
    border-radius: 16px;
    overflow: hidden;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    position: relative;
    
    &:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 30px rgba(0, 0, 0, 0.15);
    }
`;

// Изображение проекта (добавим для красоты)
export const ProjectImage = styled.div`
    height: 200px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    
    // Декоративный элемент
    &::before {
        content: '📁';
        font-size: 4rem;
        opacity: 0.3;
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
    }
    
    p {
        color: #666;
        line-height: 1.6;
        margin-bottom: 1rem;
        font-size: 0.95rem;
    }
`;

// Обновляем ProjectLink для работы с Link из react-router-dom
export const ProjectLink = styled(Link)`  // ← изменено с styled.a на styled(Link)
    text-decoration: none;
    display: inline-block;
    
    h3 {
        position: relative;
        display: inline-block;
        
        &::after {
            content: '';
            position: absolute;
            bottom: -5px;
            left: 0;
            width: 0;
            height: 2px;
            background: linear-gradient(90deg, #667eea, #764ba2);
            transition: width 0.3s ease;
        }
    }
    
    &:hover h3 {
        color: #667eea;
        
        &::after {
            width: 100%;
        }
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

// Кнопка "Подробнее" (опционально)
export const DetailsButton = styled.button`
    background: transparent;
    border: 2px solid #667eea;
    color: #667eea;
    padding: 0.5rem 1rem;
    border-radius: 25px;
    cursor: pointer;
    font-weight: 600;
    margin-top: 1rem;
    transition: all 0.3s ease;
    width: 100%;
    
    &:hover {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-color: transparent;
    }
`;

// Иконка внешней ссылки
export const ExternalIcon = styled.span`
    margin-left: 0.5rem;
    font-size: 0.9rem;
    display: inline-block;
    transition: transform 0.3s ease;
    
    ${ProjectLink}:hover & {
        transform: translateX(3px);
    }
`;