// src/pages/signalsPages/TradesPage.styles.jsx
import styled from 'styled-components';

export const PageContainer = styled.div`
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
    background: #f8f9fa;
    min-height: 100vh;
    color: #1f2937;
`;

export const Header = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding: 20px;
    background: white;
    border-radius: 12px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

    h2 {
        color: #1f2937;
        margin: 0;
        font-size: 24px;
    }

    @media (max-width: 768px) {
        flex-direction: column;
        gap: 12px;
        
        h2 {
            font-size: 18px;
            text-align: center;
        }
    }
`;

export const BackButton = styled.button`
    padding: 8px 20px;
    background: #6b7280;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 600;
    transition: all 0.3s ease;
    
    &:hover {
        background: #4b5563;
        transform: translateY(-2px);
    }

    &:active {
        transform: translateY(0);
    }
`;

export const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
    gap: 16px;
    margin-bottom: 24px;

    @media (max-width: 480px) {
        grid-template-columns: repeat(2, 1fr);
        gap: 10px;
    }
`;

export const StatCard = styled.div`
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    text-align: center;
    
    label {
        font-size: 11px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        display: block;
        margin-bottom: 4px;
    }
    
    value {
        font-size: 22px;
        font-weight: 700;
        color: #1f2937;
        display: block;
    }

    @media (max-width: 480px) {
        padding: 12px 8px;
        
        value {
            font-size: 18px;
        }
    }
`;

export const ChartCard = styled.div`
    background: white;
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    margin-bottom: 24px;
    
    h3 {
        font-size: 18px;
        color: #1f2937;
        margin-bottom: 20px;
        font-weight: 600;
        text-align: center;
        margin: 0;
    }

    @media (max-width: 768px) {
        padding: 16px;
    }
`;

export const ControlsContainer = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;
    flex-wrap: wrap;
    gap: 12px;

    @media (max-width: 480px) {
        justify-content: center;
    }
`;

export const LimitGroup = styled.div`
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    
    span {
        color: #6b7280;
        font-size: 13px;
        font-weight: 500;
        margin-right: 4px;
    }

    @media (max-width: 480px) {
        justify-content: center;
        width: 100%;
    }
`;

export const LimitButton = styled.button`
    padding: 4px 12px;
    border: 1px solid ${props => props.active ? '#8b5cf6' : '#d1d5db'};
    background: ${props => props.active ? '#8b5cf6' : 'white'};
    color: ${props => props.active ? 'white' : '#374151'};
    border-radius: 4px;
    cursor: pointer;
    font-size: 13px;
    font-weight: ${props => props.active ? '600' : '400'};
    transition: all 0.2s ease;
    min-width: 40px;
    
    &:hover:not(:disabled) {
        border-color: #8b5cf6;
        background: ${props => props.active ? '#7c3aed' : '#f3f0ff'};
    }

    &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    @media (max-width: 480px) {
        padding: 4px 10px;
        font-size: 12px;
        min-width: 36px;
    }
`;

export const LoadingContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    font-size: 18px;
    color: #1f2937;
`;

export const ErrorContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    font-size: 18px;
    color: #dc2626;
    text-align: center;
    padding: 20px;
`;

export const TradesTable = styled.div`
    overflow-x: auto;
    margin-top: 16px;
    
    table {
        width: 100%;
        border-collapse: collapse;
        color: #1f2937;
        font-size: 14px;
    }
    
    thead {
        background: #f3f4f6;
    }
    
    th {
        padding: 12px;
        text-align: left;
        font-size: 12px;
        font-weight: 600;
        color: #374151;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        white-space: nowrap;
    }
    
    td {
        padding: 10px 12px;
        border-bottom: 1px solid #e5e7eb;
        color: #1f2937;
    }
    
    tr:hover td {
        background: #f9fafb;
    }

    @media (max-width: 480px) {
        font-size: 12px;
        
        th, td {
            padding: 8px;
        }
    }
`;

export const ChartContainer = styled.div`
    height: 400px;
    position: relative;

    @media (max-width: 768px) {
        height: 300px;
    }

    @media (max-width: 480px) {
        height: 250px;
    }
`;

export const PaginationContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 6px;
    margin-top: 20px;
    padding-top: 16px;
    border-top: 1px solid #e5e7eb;
    flex-wrap: wrap;

    @media (max-width: 480px) {
        gap: 4px;
    }
`;

export const PageButton = styled.button`
    padding: 6px 12px;
    border: 1px solid ${props => props.active ? '#8b5cf6' : '#d1d5db'};
    background: ${props => props.active ? '#8b5cf6' : 'white'};
    color: ${props => props.active ? 'white' : '#374151'};
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    min-width: 36px;
    transition: all 0.2s ease;
    
    &:hover:not(:disabled) {
        border-color: #8b5cf6;
        background: ${props => props.active ? '#7c3aed' : '#f3f0ff'};
    }
    
    &:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    @media (max-width: 480px) {
        padding: 4px 8px;
        font-size: 12px;
        min-width: 30px;
    }
`;