import styled from 'styled-components';

export const HomeContainer = styled.div`
    min-height: 100vh;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 40px 20px;
`;

export const Hero = styled.div`
    text-align: center;
    padding: 60px 20px;
    max-width: 800px;
    margin: 0 auto;

    h1 {
        font-size: 48px;
        color: white;
        margin-bottom: 20px;
        font-weight: bold;
        
        @media (max-width: 768px) {
            font-size: 32px;
        }
    }

    p {
        font-size: 20px;
        color: rgba(255, 255, 255, 0.9);
        margin-bottom: 40px;
        line-height: 1.5;
        
        @media (max-width: 768px) {
            font-size: 16px;
        }
    }
`;

export const HeroButtons = styled.div`
    display: flex;
    gap: 20px;
    justify-content: center;
    flex-wrap: wrap;
`;

const BaseButton = styled.div`
    display: inline-block;
    padding: 12px 24px;
    border-radius: 8px;
    text-decoration: none;
    font-weight: 600;
    transition: all 0.3s ease;
    cursor: pointer;
    
    &:hover {
        transform: translateY(-2px);
    }
`;

export const PrimaryButton = styled(BaseButton)`
    background-color: #007bff;
    color: white;
    border: 2px solid #007bff;
    
    &:hover {
        background-color: #0056b3;
        border-color: #0056b3;
    }
`;

export const SecondaryButton = styled(BaseButton)`
    background-color: transparent;
    color: white;
    border: 2px solid white;
    
    &:hover {
        background-color: white;
        color: #667eea;
    }
`;

export const Features = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
    max-width: 1200px;
    margin: 0 auto;
    padding: 40px 20px;
`;

export const Feature = styled.div`
    background: white;
    border-radius: 16px;
    padding: 30px;
    text-align: center;
    transition: transform 0.3s ease;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
    
    &:hover {
        transform: translateY(-5px);
    }

    h3 {
        font-size: 24px;
        color: #333;
        margin-bottom: 15px;
    }

    p {
        color: #666;
        line-height: 1.6;
        font-size: 16px;
    }
`;