// ContactSection.styles.js
import styled from 'styled-components';

// Основная секция контактов
export const ContactSectionMain = styled.section`
    padding: 80px 20px;
    background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
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
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0) 70%);
        animation: rotate 30s linear infinite;
    }
    
    &::after {
        content: '✉️';
        position: absolute;
        bottom: 20px;
        right: 20px;
        font-size: 100px;
        opacity: 0.05;
        pointer-events: none;
    }
    
    @keyframes rotate {
        from {
            transform: rotate(0deg);
        }
        to {
            transform: rotate(360deg);
        }
    }
    
    @media (max-width: 768px) {
        padding: 60px 20px;
    }
`;

// Контейнер
export const Container = styled.div`
    max-width: 800px;
    margin: 0 auto;
    text-align: center;
    position: relative;
    z-index: 1;
    
    h2 {
        font-size: 2.5rem;
        color: white;
        margin-bottom: 1rem;
        animation: fadeInDown 0.8s ease;
        
        @media (max-width: 768px) {
            font-size: 2rem;
        }
    }
    
    p {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 2.5rem;
        animation: fadeInUp 0.8s ease;
        
        @media (max-width: 768px) {
            font-size: 1rem;
        }
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
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

// Контейнер ссылок контактов
export const ContactLinks = styled.div`
    display: flex;
    flex-direction: column;
    gap: 1rem;
    max-width: 400px;
    margin: 0 auto;
    animation: fadeInUp 0.8s ease 0.2s both;
`;

// Элемент контакта
export const ContactItem = styled.a`
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    color: white;
    text-decoration: none;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    font-size: 1.1rem;
    transition: all 0.3s ease;
    border: 1px solid rgba(255, 255, 255, 0.2);
    
    &:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateX(10px);
        border-color: rgba(255, 255, 255, 0.4);
    }
    
    @media (max-width: 768px) {
        font-size: 0.9rem;
        padding: 0.8rem 1rem;
        gap: 0.8rem;
    }
`;

// Иконка контакта (отдельный компонент для иконки)
export const ContactIcon = styled.span`
    font-size: 1.5rem;
    
    @media (max-width: 768px) {
        font-size: 1.2rem;
    }
`;

// Текст контакта
export const ContactText = styled.span`
    flex: 1;
    text-align: left;
    word-break: break-all;
`;

// Социальные сети (дополнительно)
export const SocialGrid = styled.div`
    display: flex;
    justify-content: center;
    gap: 1.5rem;
    margin-top: 2rem;
    animation: fadeInUp 0.8s ease 0.4s both;
`;

export const SocialLink = styled.a`
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    color: white;
    text-decoration: none;
    padding: 0.8rem 1.2rem;
    border-radius: 12px;
    transition: all 0.3s ease;
    font-size: 0.9rem;
    border: 1px solid rgba(255, 255, 255, 0.2);
    
    &:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: translateY(-3px);
    }
`;

// Кнопка копирования (бонус)
export const CopyButton = styled.button`
    background: rgba(255, 255, 255, 0.1);
    color: white;
    border: 1px solid rgba(255, 255, 255, 0.2);
    padding: 0.3rem 0.8rem;
    border-radius: 6px;
    cursor: pointer;
    font-size: 0.8rem;
    transition: all 0.3s ease;
    margin-left: 0.5rem;
    
    &:hover {
        background: rgba(255, 255, 255, 0.2);
        transform: scale(1.05);
    }
`;