// SkillSection.styles.js
import styled from 'styled-components';

// Основная секция навыков
export const ServicesSection = styled.section`
    padding: 80px 20px;
    background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
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

// Сетка карточек
export const ServicesGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
    
    @media (max-width: 768px) {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
`;

// Карточка услуги/навыка
export const ServiceCard = styled.div`
    background: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    transition: all 0.3s ease;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    cursor: pointer;
    
    &:hover {
        transform: translateY(-10px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.15);
    }
    
    h3 {
        font-size: 1.5rem;
        color: #1e3c72;
        margin: 1rem 0;
        transition: color 0.3s ease;
    }
    
    p {
        color: #666;
        line-height: 1.6;
        font-size: 1rem;
    }
    
    &:hover h3 {
        color: #667eea;
    }
`;

// Иконка сервиса
export const ServiceIcon = styled.div`
    font-size: 3.5rem;
    margin-bottom: 1rem;
    display: inline-block;
    animation: float 3s ease-in-out infinite;
    
    @keyframes float {
        0% {
            transform: translateY(0px);
        }
        50% {
            transform: translateY(-10px);
        }
        100% {
            transform: translateY(0px);
        }
    }
`;

// Дополнительно: добавим еще стилей для расширения
export const TechStack = styled.div`
    margin-top: 1rem;
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 0.5rem;
`;

export const TechBadge = styled.span`
    background: #f0f0f0;
    color: #667eea;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: 500;
    transition: all 0.3s ease;
    
    &:hover {
        background: #667eea;
        color: white;
        transform: scale(1.05);
    }
`;

// Декоративный элемент
export const DecorativeLine = styled.div`
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
`;