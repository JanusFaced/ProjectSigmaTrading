import styled from 'styled-components';

export const LoginContainer = styled.div`
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px;

    background:
        radial-gradient(circle at 15% 20%, rgba(37, 99, 235, 0.16), transparent 32%),
        radial-gradient(circle at 85% 80%, rgba(14, 165, 233, 0.1), transparent 30%),
        #090d14;
`;

export const LoginCard = styled.div`
    width: 100%;
    max-width: 430px;
    padding: 42px 40px 34px;

    background: rgba(17, 24, 39, 0.94);
    border: 1px solid rgba(148, 163, 184, 0.16);
    border-radius: 16px;
    box-shadow:
        0 24px 70px rgba(0, 0, 0, 0.45),
        0 0 0 1px rgba(255, 255, 255, 0.02);
`;

export const LoginTitle = styled.h2`
    margin: 0 0 10px;

    color: #f8fafc;
    text-align: center;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;
`;

export const LoginSubtitle = styled.p`
    margin: 0 0 30px;

    color: #94a3b8;
    text-align: center;
    font-size: 14px;
    line-height: 1.6;
`;

export const FormGroup = styled.div`
    margin-bottom: 22px;
`;

export const Label = styled.label`
    display: block;
    margin-bottom: 9px;

    color: #cbd5e1;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.2px;
`;

export const Input = styled.input`
    box-sizing: border-box;
    width: 100%;
    min-height: 50px;
    padding: 13px 15px;

    color: #f8fafc;
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 9px;
    outline: none;

    font-family: inherit;
    font-size: 15px;
    transition:
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        background 0.2s ease;

    &::placeholder {
        color: #64748b;
    }

    &:hover:not(:disabled) {
        border-color: #475569;
    }

    &:focus {
        background: #111c31;
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.16);
    }

    &:disabled {
        color: #64748b;
        background: #111827;
        cursor: not-allowed;
        opacity: 0.7;
    }
`;

export const Button = styled.button`
    width: 100%;
    min-height: 50px;
    padding: 13px 16px;

    color: #ffffff;
    background: #2563eb;
    border: 1px solid #3b82f6;
    border-radius: 9px;

    font-family: inherit;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;

    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        transform 0.2s ease;

    &:hover:not(:disabled) {
        background: #1d4ed8;
        border-color: #60a5fa;
        box-shadow: 0 8px 24px rgba(37, 99, 235, 0.28);
        transform: translateY(-1px);
    }

    &:active:not(:disabled) {
        background: #1e40af;
        transform: translateY(0);
    }

    &:disabled {
        color: #94a3b8;
        background: #1e293b;
        border-color: #334155;
        cursor: not-allowed;
        opacity: 0.8;
    }
`;

export const ErrorMessage = styled.div`
    margin-bottom: 20px;
    padding: 12px 14px;

    color: #fca5a5;
    background: rgba(127, 29, 29, 0.24);
    border: 1px solid rgba(248, 113, 113, 0.32);
    border-radius: 8px;

    font-size: 13px;
    line-height: 1.5;
    text-align: center;
`;

export const InfoText = styled.div`
    margin-top: 22px;

    color: #64748b;
    font-size: 12px;
    text-align: center;
    letter-spacing: 0.2px;

    code {
        padding: 3px 7px;

        color: #94a3b8;
        background: #1e293b;
        border-radius: 4px;
        font-size: 12px;
    }
`;
