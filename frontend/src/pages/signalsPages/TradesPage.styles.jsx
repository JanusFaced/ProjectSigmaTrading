// src/pages/signalsPages/TradesPage.styles.jsx
import styled from 'styled-components';

export const PageContainer = styled.div`
    padding: 24px;
    max-width: 1200px;
    margin: 0 auto;
    background: #f8f9fa;
    min-height: 100vh;
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
`;

export const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
`;

export const StatCard = styled.div`
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    text-align: center;
    
    label {
        font-size: 12px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        font-weight: 600;
        display: block;
        margin-bottom: 4px;
    }
    
    value {
        font-size: 24px;
        font-weight: 700;
        color: #1f2937;
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
    }
`;

export const LoadingContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    font-size: 18px;
    color: #6b7280;
`;

export const ErrorContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 400px;
    font-size: 18px;
    color: #ef4444;
`;

export const TradesTable = styled.div`
    overflow-x: auto;
    margin-top: 24px;
    
    table {
        width: 100%;
        border-collapse: collapse;
    }
    
    thead {
        background: #f3f4f6;
    }
    
    th {
        padding: 10px;
        text-align: left;
        font-size: 12px;
        font-weight: 600;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    td {
        padding: 10px;
        border-bottom: 1px solid #e5e7eb;
    }
    
    tr:hover td {
        background: #f9fafb;
    }
`;

export const ChartContainer = styled.div`
    height: 400px;
    position: relative;
`;