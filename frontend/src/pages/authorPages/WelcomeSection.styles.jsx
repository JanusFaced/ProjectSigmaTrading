// WelcomeSection.styles.js
import styled from 'styled-components';

// Основной контейнер Welcome секции
export const WelcomeHeader = styled.header`
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    position: relative;
    overflow: hidden;
    
    // Декоративные элементы фона
    &::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 70%);
        animation: rotate 20s linear infinite;
    }
    
    @keyframes rotate {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
`;

// Контейнер для контента
export const Container = styled.div`
    max-width: 800px;
    margin: 0 auto;
    padding: 2rem;
    text-align: center;
    position: relative;
    z-index: 1;
    
    h1 {
        font-size: 3.5rem;
        color: white;
        margin-bottom: 1.5rem;
        font-weight: bold;
        animation: fadeInUp 0.8s ease;
        
        @media (max-width: 768px) {
            font-size: 2rem;
        }
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

// Тэглайн
export const Tagline = styled.p`
    font-size: 1.5rem;
    color: rgba(255, 255, 255, 0.95);
    line-height: 1.6;
    animation: fadeInUp 0.8s ease 0.2s both;
    
    @media (max-width: 768px) {
        font-size: 1.1rem;
    }
`;

// Декоративная кнопка (опционально, добавим для красоты)
export const ScrollButton = styled.button`
    margin-top: 3rem;
    background: transparent;
    border: 2px solid white;
    color: white;
    padding: 0.8rem 2rem;
    font-size: 1.1rem;
    border-radius: 50px;
    cursor: pointer;
    transition: all 0.3s ease;
    animation: fadeInUp 0.8s ease 0.4s both;
    
    &:hover {
        background: white;
        color: #667eea;
        transform: translateY(-3px);
    }
    
    @media (max-width: 768px) {
        padding: 0.6rem 1.5rem;
        font-size: 1rem;
    }
`;