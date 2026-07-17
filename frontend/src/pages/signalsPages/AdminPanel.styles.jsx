import styled from 'styled-components';

export const AdminContainer = styled.div`
    padding: 40px 20px;
    max-width: 1400px;
    margin: 0 auto;
`;

export const AdminHeader = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 30px;
    flex-wrap: wrap;
    gap: 15px;
`;

export const Title = styled.h1`
    display: flex;
    align-items: center;
    gap: 12px;
    color: #ffffff;
    font-size: 28px;
    margin: 0;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
    
    .icon {
        font-size: 32px;
        filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
    }
`;

export const HeaderActions = styled.div`
    display: flex;
    gap: 12px;
    align-items: center;
`;

export const Button = styled.button`
    padding: 10px 20px;
    border: none;
    border-radius: 10px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    font-size: 14px;
    display: flex;
    align-items: center;
    gap: 8px;
    
    &:hover {
        transform: translateY(-2px);
    }
`;

export const RefreshButton = styled(Button)`
    background: #667eea;
    color: white;
    
    &:hover {
        background: #5a6fd6;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
`;

export const LogoutButton = styled(Button)`
    background: #dc3545;
    color: white;
    
    &:hover {
        background: #c82333;
        box-shadow: 0 4px 15px rgba(220, 53, 69, 0.4);
    }
`;

export const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 30px;
`;

export const StatCard = styled.div`
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    text-align: center;
    
    .number {
        font-size: 32px;
        font-weight: 700;
        color: #667eea;
    }
    
    .label {
        color: #666;
        font-size: 14px;
        margin-top: 5px;
    }
`;

export const Section = styled.div`
    background: white;
    border-radius: 15px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
    overflow: hidden;
    margin-bottom: 30px;
`;

export const SectionHeader = styled.div`
    padding: 20px 25px;
    background: ${props => props.color || '#667eea'};
    color: white;
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
        margin: 0;
        font-size: 18px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .badge {
        background: rgba(255, 255, 255, 0.2);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 14px;
    }
`;

export const TableWrapper = styled.div`
    overflow-x: auto;
    padding: 0;
`;

export const Table = styled.table`
    width: 100%;
    border-collapse: collapse;
    
    th {
        background: #f0f2f5; /* СВЕТЛО-СЕРЫЙ ФОН ДЛЯ ЗАГОЛОВКОВ */
        padding: 15px 20px;
        text-align: left;
        font-weight: 700; /* ЖИРНЕЕ */
        color: #1a1a2e; /* ТЕМНО-СИНИЙ, ПОЧТИ ЧЕРНЫЙ */
        border-bottom: 2px solid #d1d5db;
        white-space: nowrap;
        font-size: 14px;
        letter-spacing: 0.3px;
    }
    
    td {
        padding: 14px 20px;
        border-bottom: 1px solid #e5e7eb;
        vertical-align: middle;
        color: #1f2937; /* ТЕМНО-СЕРЫЙ ДЛЯ ТЕКСТА */
        font-size: 14px;
    }
    
    /* СТРОКИ ПРИ НАВЕДЕНИИ */
    tbody tr:hover td {
        background: #f8fafc;
    }
    
    /* ЧЕРЕЗ СТРОКУ (ZEBRA) */
    tbody tr:nth-child(even) td {
        background: #fafbfc;
    }
    
    tbody tr:nth-child(even):hover td {
        background: #f1f5f9;
    }
    
    /* СТРАТЕГИЯ - ЖИРНЫЙ ТЕКСТ */
    td:first-child + td {
        font-weight: 600;
        color: #0f172a;
    }
    
    /* ID - ЦВЕТНОЙ БЭЙДЖ */
    td:first-child {
        font-weight: 700;
        color: #4b5563;
    }
`;

export const StatusBadge = styled.span`
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 600;
    background: ${props => props.active ? '#d4edda' : '#f8d7da'};
    color: ${props => props.active ? '#155724' : '#721c24'};
`;

export const DeleteButton = styled.button`
    padding: 6px 14px;
    background: #dc3545;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    font-size: 13px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    gap: 5px;
    font-weight: 500;
    
    &:hover {
        background: #c82333;
        transform: scale(1.05);
    }
`;

export const LoadingSpinner = styled.div`
    text-align: center;
    padding: 40px;
    
    .spinner {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #667eea;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 10px;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
`;

export const EmptyState = styled.div`
    text-align: center;
    padding: 40px;
    color: #6b7280; /* ТЕМНО-СЕРЫЙ ВМЕСТО СВЕТЛОГО */
    
    .icon {
        font-size: 48px;
        margin-bottom: 10px;
        opacity: 0.5;
    }
`;