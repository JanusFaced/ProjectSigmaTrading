import styled from 'styled-components';

export const PageContainer = styled.div`
    max-width: 1400px;
    margin: 0 auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
    gap: 24px;
`;

export const Header = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 16px;

    h2 {
        margin: 0;
        font-size: 22px;
        color: #111827;
    }
`;

export const BackButton = styled.button`
    background: #f3f4f6;
    border: none;
    border-radius: 8px;
    padding: 8px 16px;
    cursor: pointer;
    font-size: 14px;
    color: #374151;
    transition: background 0.2s;

    &:hover {
        background: #e5e7eb;
    }
`;

export const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 16px;
`;

export const StatCard = styled.div`
    background: white;
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);

    label {
        display: block;
        font-size: 12px;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    value {
        display: block;
        font-size: 22px;
        font-weight: 700;
        color: #111827;
    }
`;

export const ChartCard = styled.div`
    background: white;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);

    h3 {
        margin: 0 0 16px 0;
        font-size: 16px;
        color: #111827;
    }
`;

export const ChartContainer = styled.div`
    height: 380px;
    position: relative;
`;

export const ControlsContainer = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
    margin-bottom: 16px;

    h3 {
        margin: 0;
        font-size: 16px;
        color: #111827;
    }
`;

export const LimitGroup = styled.div`
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 13px;
    color: #6b7280;
`;

export const LimitButton = styled.button`
    border: 1px solid #e5e7eb;
    background: ${({ active }) => (active ? '#8b5cf6' : 'white')};
    color: ${({ active }) => (active ? 'white' : '#374151')};
    padding: 4px 10px;
    border-radius: 6px;
    cursor: pointer;
    font-size: 12px;

    &:hover {
        border-color: #8b5cf6;
    }
`;

export const TradesTable = styled.div`
    overflow-x: auto;

    table {
        width: 100%;
        border-collapse: collapse;
        font-size: 14px;
    }

    th {
        text-align: left;
        padding: 10px 12px;
        background: #f9fafb;
        color: #6b7280;
        font-weight: 600;
        font-size: 12px;
        text-transform: uppercase;
    }

    td {
        padding: 10px 12px;
        border-top: 1px solid #f3f4f6;
        color: #111827;
    }
`;

export const PaginationContainer = styled.div`
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 16px;
    gap: 4px;
`;

export const PageButton = styled.button`
    min-width: 34px;
    height: 34px;
    border-radius: 6px;
    border: 1px solid #e5e7eb;
    background: ${({ active }) => (active ? '#8b5cf6' : 'white')};
    color: ${({ active }) => (active ? 'white' : '#374151')};
    cursor: pointer;
    font-size: 13px;

    &:disabled {
        opacity: 0.4;
        cursor: not-allowed;
    }

    &:hover:not(:disabled) {
        border-color: #8b5cf6;
    }
`;

export const LoadingContainer = styled.div`
    padding: 60px;
    text-align: center;
    font-size: 16px;
    color: #6b7280;
`;

export const ErrorContainer = styled.div`
    padding: 60px;
    text-align: center;
    color: #ef4444;
`;

export const EmptyContainer = styled.div`
    padding: 40px;
    text-align: center;
    color: #6b7280;
`;