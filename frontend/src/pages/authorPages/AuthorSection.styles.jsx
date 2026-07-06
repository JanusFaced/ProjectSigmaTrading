// AuthorSection.styles.js
import styled from 'styled-components';
import { NavLink } from 'react-router-dom';

// Основная секция об авторе
export const HeroSection = styled.section`
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    position: relative;
    padding: 80px 20px;
    
    // Декоративный элемент
    &::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2, #667eea);
    }
`;

// Контейнер для контента
export const Container = styled.div`
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
    position: relative;
    z-index: 1;
    
    h1 {
        font-size: 3.5rem;
        color: #1e3c72;
        margin-bottom: 1rem;
        font-weight: bold;
        animation: slideInLeft 0.8s ease;
        
        @media (max-width: 768px) {
            font-size: 2.5rem;
        }
    }
    
    @keyframes slideInLeft {
        from {
            opacity: 0;
            transform: translateX(-50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;

// Теглайн автора
export const AuthorTagline = styled.p`
    font-size: 1.8rem;
    color: #667eea;
    margin-bottom: 1.5rem;
    font-weight: 600;
    animation: slideInRight 0.8s ease;
    
    @media (max-width: 768px) {
        font-size: 1.3rem;
    }
    
    @keyframes slideInRight {
        from {
            opacity: 0;
            transform: translateX(50px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
`;

// Описание
export const Description = styled.p`
    font-size: 1.2rem;
    color: #555;
    line-height: 1.8;
    margin-bottom: 2rem;
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    animation: fadeInUp 0.8s ease 0.2s both;
    
    @media (max-width: 768px) {
        font-size: 1rem;
        line-height: 1.6;
    }
    
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
`;

export const CTAButton = styled(NavLink)`
    display: inline-block;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-decoration: none;
    padding: 1rem 2rem;
    font-size: 1.1rem;
    font-weight: 600;
    border-radius: 50px;
    transition: all 0.3s ease;
    animation: fadeInUp 0.8s ease 0.4s both;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    
    &:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.3);
    }
    
    @media (max-width: 768px) {
        padding: 0.8rem 1.5rem;
        font-size: 1rem;
    }
`;

// Дополнительные элементы (опционально)
export const SocialLinks = styled.div`
    margin-top: 2rem;
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    animation: fadeInUp 0.8s ease 0.6s both;
`;

export const SocialIcon = styled.a`
    color: #667eea;
    font-size: 1.5rem;
    transition: all 0.3s ease;
    
    &:hover {
        color: #764ba2;
        transform: translateY(-3px);
    }
`;

// Счетчик или статистика (опционально)
export const Stats = styled.div`
    display: flex;
    justify-content: center;
    gap: 3rem;
    margin-top: 3rem;
    animation: fadeInUp 0.8s ease 0.8s both;
    
    @media (max-width: 768px) {
        gap: 1.5rem;
        flex-wrap: wrap;
    }
`;

export const StatItem = styled.div`
    text-align: center;
    
    h3 {
        font-size: 2rem;
        color: #667eea;
        margin-bottom: 0.5rem;
        
        @media (max-width: 768px) {
            font-size: 1.5rem;
        }
    }
    
    p {
        color: #666;
        font-size: 0.9rem;
    }
`;