import styled from 'styled-components';

export const ModalOverlay = styled.div`
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(5px);
    display: ${props => props.show ? 'flex' : 'none'};
    align-items: center;
    justify-content: center;
    z-index: 9999;
    padding: 20px;
`;

export const ModalContent = styled.div`
    background: white;
    border-radius: 20px;
    max-width: 500px;
    width: 100%;
    padding: 30px;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: slideIn 0.3s ease;
    
    @keyframes slideIn {
        from {
            transform: translateY(-30px);
            opacity: 0;
        }
        to {
            transform: translateY(0);
            opacity: 1;
        }
    }
`;

export const ModalHeader = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    
    h3 {
        margin: 0;
        color: #dc3545;
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 22px;
    }
`;

export const CloseButton = styled.button`
    background: none;
    border: none;
    font-size: 28px;
    cursor: pointer;
    color: #999;
    transition: color 0.3s ease;
    
    &:hover {
        color: #333;
    }
`;

export const ModalBody = styled.div`
    margin-bottom: 25px;
    
    p {
        margin: 10px 0;
        color: #555;
        line-height: 1.6;
    }
`;

export const InfoBox = styled.div`
    background: #fff3cd;
    border: 1px solid #ffc107;
    border-radius: 10px;
    padding: 15px;
    margin: 15px 0;
    
    strong {
        display: block;
        font-size: 16px;
        color: #856404;
        margin-bottom: 5px;
    }
    
    .detail {
        color: #856404;
        font-size: 14px;
    }
`;

export const WarningText = styled.p`
    color: #dc3545;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 15px 0;
`;

export const ModalFooter = styled.div`
    display: flex;
    gap: 12px;
    justify-content: flex-end;
`;

export const CancelButton = styled.button`
    padding: 10px 25px;
    background: #6c757d;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    
    &:hover {
        background: #5a6268;
        transform: translateY(-2px);
    }
`;

export const ConfirmButton = styled.button`
    padding: 10px 25px;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 10px;
    cursor: pointer;
    font-weight: 600;
    transition: all 0.3s ease;
    display: flex;
    align-items: center;
    gap: 8px;
    
    &:hover {
        background: #c82333;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
    }
`;