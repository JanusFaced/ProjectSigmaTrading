// AboutPage.styles.js
import styled from 'styled-components';

// Основной контейнер страницы
export const AboutContainer = styled.div`
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px 20px;
    
    h1 {
        text-align: center;
        color: white;
        font-size: 42px;
        margin-bottom: 50px;
        font-weight: bold;
        
        @media (max-width: 768px) {
            font-size: 32px;
            margin-bottom: 30px;
        }
    }
    
    h2 {
        font-size: 28px;
        margin-bottom: 20px;
        color: #333;
        
        @media (max-width: 768px) {
            font-size: 24px;
        }
    }
`;

// Секция (общий стиль для всех секций)
export const Section = styled.section`
    background: white;
    border-radius: 16px;
    padding: 30px;
    margin-bottom: 30px;
    max-width: 1000px;
    margin-left: auto;
    margin-right: auto;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    transition: transform 0.3s ease;
    
    &:hover {
        transform: translateY(-3px);
    }
    
    @media (max-width: 768px) {
        padding: 20px;
        margin-bottom: 20px;
    }
    
    p {
        line-height: 1.6;
        color: #555;
        margin-bottom: 15px;
        font-size: 16px;
        
        &:last-child {
            margin-bottom: 0;
        }
    }
`;

// Карточка автора
export const AuthorCard = styled.div`
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px;
    padding: 20px;
    margin-top: 10px;
`;

// Детали автора
export const AuthorDetails = styled.div`
    p {
        margin: 12px 0;
        font-size: 16px;
        
        strong {
            color: #333;
            min-width: 80px;
            display: inline-block;
        }
    }
`;

// Карточка реквизитов
export const RequisitesCard = styled.div`
    background: #f8f9fa;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #e9ecef;
`;

// Элемент реквизита
export const RequisiteItem = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #e9ecef;
    
    &:last-child {
        border-bottom: none;
    }
    
    @media (max-width: 768px) {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
`;

// Лейбл реквизита
export const RequisiteLabel = styled.span`
    font-weight: bold;
    color: #667eea;
    font-size: 16px;
`;

// Значение реквизита
export const RequisiteValue = styled.span`
    color: #333;
    font-family: monospace;
    font-size: 14px;
    background: white;
    padding: 4px 8px;
    border-radius: 6px;
    
    @media (max-width: 768px) {
        width: 100%;
        word-break: break-all;
    }
`;

// Примечание к реквизитам
export const RequisitesNote = styled.p`
    font-size: 12px;
    color: #999;
    margin-top: 15px !important;
    text-align: center;
    font-style: italic;
`;

// Секция контактов
export const ContactSection = styled(Section)`
    a {
        color: #667eea;
        text-decoration: none;
        transition: color 0.3s ease;
        word-break: break-all;
        
        &:hover {
            color: #764ba2;
            text-decoration: underline;
        }
    }
    
    p {
        margin: 15px 0;
        
        &:last-child {
            margin-bottom: 0;
        }
    }
`;

// Стилизованный код для адресов (опционально)
export const AddressCode = styled.code`
    background: #f1f3f4;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 14px;
    color: #d63384;
`;

// Бонус: декоративный элемент для секций
export const SectionIcon = styled.span`
    font-size: 32px;
    margin-right: 10px;
    vertical-align: middle;
`;

// Контейнер для заголовка с иконкой
export const SectionHeader = styled.div`
    display: flex;
    align-items: center;
    margin-bottom: 20px;
    
    h2 {
        margin-bottom: 0;
    }
`;