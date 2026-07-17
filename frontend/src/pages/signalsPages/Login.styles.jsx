import styled from 'styled-components';

export const LoginContainer = styled.div`
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 20px;
`;

export const LoginCard = styled.div`
    background: white;
    border-radius: 20px;
    padding: 40px;
    width: 100%;
    max-width: 420px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
`;

export const LoginTitle = styled.h2`
    text-align: center;
    color: #333;
    margin-bottom: 10px;
    font-size: 28px;
    font-weight: 700;
`;

export const LoginSubtitle = styled.p`
    text-align: center;
    color: #666;
    margin-bottom: 30px;
    font-size: 14px;
`;

export const FormGroup = styled.div`
    margin-bottom: 20px;
`;

export const Label = styled.label`
    display: block;
    margin-bottom: 8px;
    color: #555;
    font-weight: 500;
    font-size: 14px;
`;

export const Input = styled.input`
    width: 100%;
    padding: 12px 16px;
    border: 2px solid #e1e5e9;
    border-radius: 10px;
    font-size: 16px;
    transition: all 0.3s ease;
    
    &:focus {
        outline: none;
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    &:disabled {
        background: #f5f5f5;
        cursor: not-allowed;
    }
`;

export const Button = styled.button`
    width: 100%;
    padding: 14px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    border-radius: 10px;
    font-size: 16px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    
    &:hover:not(:disabled) {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    &:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
`;

export const ErrorMessage = styled.div`
    background: #fee;
    color: #c33;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 20px;
    font-size: 14px;
    text-align: center;
    border: 1px solid #fcc;
`;

export const InfoText = styled.div`
    text-align: center;
    margin-top: 20px;
    font-size: 13px;
    color: #999;
    
    code {
        background: #f5f5f5;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 12px;
        color: #666;
    }
`;