import styled from 'styled-components';

export const AdminContainer = styled.div`
    box-sizing: border-box;
    width: 100%;
    min-height: 100vh;
    max-width: 1440px;
    margin: 0 auto;
    padding: 34px 28px 50px;

    color: #e2e8f0;
`;

export const AdminHeader = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 30px;
    flex-wrap: wrap;
`;

export const Title = styled.h1`
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0;

    color: #f8fafc;
    font-size: 28px;
    font-weight: 700;
    letter-spacing: -0.5px;

    .icon {
        font-size: 29px;
        filter: grayscale(0.15);
    }

    @media (max-width: 600px) {
        font-size: 24px;

        .icon {
            font-size: 25px;
        }
    }
`;

export const HeaderActions = styled.div`
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;

    @media (max-width: 600px) {
        width: 100%;

        button {
            flex: 1;
        }
    }
`;

export const Button = styled.button`
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;

    min-height: 40px;
    padding: 10px 16px;

    border: 1px solid transparent;
    border-radius: 8px;

    font-family: inherit;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;

    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        box-shadow 0.2s ease,
        transform 0.2s ease;

    &:hover {
        transform: translateY(-1px);
    }

    &:active {
        transform: translateY(0);
    }
`;

export const RefreshButton = styled(Button)`
    color: #bfdbfe;
    background: #172554;
    border-color: #1e40af;

    &:hover {
        background: #1e3a8a;
        border-color: #2563eb;
        box-shadow: 0 6px 18px rgba(37, 99, 235, 0.2);
    }
`;

export const LogoutButton = styled(Button)`
    color: #fecaca;
    background: #2a1519;
    border-color: #7f1d1d;

    &:hover {
        background: #451a1a;
        border-color: #b91c1c;
        box-shadow: 0 6px 18px rgba(220, 38, 38, 0.18);
    }
`;

export const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
    gap: 16px;
    margin-bottom: 28px;
`;

export const StatCard = styled.div`
    padding: 22px 24px;

    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);

    text-align: center;
    transition:
        border-color 0.2s ease,
        transform 0.2s ease;

    &:hover {
        border-color: #334155;
        transform: translateY(-2px);
    }

    .number {
        color: #60a5fa;
        font-size: 32px;
        font-weight: 700;
        line-height: 1.2;
    }

    .label {
        margin-top: 8px;

        color: #94a3b8;
        font-size: 13px;
        font-weight: 500;
    }
`;

export const Section = styled.div`
    margin-bottom: 28px;
    overflow: hidden;

    background: #111827;
    border: 1px solid #1f2937;
    border-radius: 12px;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.18);
`;

export const SectionHeader = styled.div`
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 15px;

    padding: 17px 22px;

    /*
     * Компонент передаёт color="#667eea".
     * Здесь он используется как декоративный верхний акцент,
     * а не как яркий фон всей шапки.
     */
    background: linear-gradient(
        90deg,
        rgba(30, 64, 175, 0.32),
        rgba(15, 23, 42, 0.7)
    );
    border-bottom: 1px solid #263449;
    border-top: 2px solid ${props => props.color || '#2563eb'};

    h3 {
        display: flex;
        align-items: center;
        gap: 9px;
        margin: 0;

        color: #f1f5f9;
        font-size: 16px;
        font-weight: 650;
    }

    .badge {
        min-width: 28px;
        padding: 4px 10px;

        color: #bfdbfe;
        background: #1e3a8a;
        border: 1px solid #2563eb;
        border-radius: 999px;

        font-size: 12px;
        font-weight: 700;
        text-align: center;
    }

    @media (max-width: 600px) {
        padding: 15px 16px;

        h3 {
            font-size: 14px;
        }
    }
`;

export const TableWrapper = styled.div`
    width: 100%;
    overflow-x: auto;
`;

export const Table = styled.table`
    width: 100%;
    min-width: 850px;
    border-collapse: collapse;

    th {
        padding: 14px 18px;

        color: #94a3b8;
        background: #0f172a;
        border-bottom: 1px solid #263449;

        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.7px;
        text-align: left;
        text-transform: uppercase;
        white-space: nowrap;
    }

    td {
        padding: 15px 18px;

        color: #cbd5e1;
        background: #111827;
        border-bottom: 1px solid #1f2937;

        font-size: 13px;
        vertical-align: middle;
        white-space: nowrap;
    }

    tbody tr {
        transition: background 0.15s ease;
    }

    tbody tr:hover td {
        background: #172033;
    }

    tbody tr:last-child td {
        border-bottom: none;
    }

    td:first-child {
        color: #64748b;
        font-weight: 700;
    }

    td:first-child + td {
        color: #f1f5f9;
        font-weight: 600;
    }

    td strong {
        font-weight: 650;
    }
`;

export const StatusBadge = styled.span`
    display: inline-flex;
    align-items: center;
    gap: 5px;

    padding: 5px 10px;

    color: ${props => props.active ? '#86efac' : '#fca5a5'};
    background: ${props =>
        props.active
            ? 'rgba(22, 101, 52, 0.28)'
            : 'rgba(127, 29, 29, 0.28)'};
    border: 1px solid ${props =>
        props.active
            ? 'rgba(34, 197, 94, 0.35)'
            : 'rgba(248, 113, 113, 0.35)'};
    border-radius: 999px;

    font-size: 11px;
    font-weight: 700;
`;

export const DeleteButton = styled.button`
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 5px;

    padding: 7px 12px;

    color: #fca5a5;
    background: #2a1519;
    border: 1px solid #7f1d1d;
    border-radius: 7px;

    font-family: inherit;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;

    transition:
        background 0.2s ease,
        border-color 0.2s ease,
        color 0.2s ease,
        transform 0.2s ease;

    &:hover {
        color: #fee2e2;
        background: #451a1a;
        border-color: #b91c1c;
        transform: translateY(-1px);
    }

    &:active {
        transform: translateY(0);
    }
`;

export const LoadingSpinner = styled.div`
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    min-height: 260px;
    padding: 40px;

    color: #94a3b8;
    text-align: center;

    p {
        margin: 14px 0 0;
        font-size: 13px;
    }

    .spinner {
        width: 36px;
        height: 36px;

        border: 3px solid #263449;
        border-top-color: #3b82f6;
        border-radius: 50%;

        animation: spin 0.8s linear infinite;
    }

    @keyframes spin {
        from {
            transform: rotate(0deg);
        }

        to {
            transform: rotate(360deg);
        }
    }
`;

export const EmptyState = styled.div`
    padding: 58px 25px;

    color: #64748b;
    text-align: center;

    .icon {
        margin-bottom: 12px;
        font-size: 42px;
        opacity: 0.6;
        filter: grayscale(0.35);
    }

    p {
        margin: 0;
        font-size: 13px;
    }
`;
