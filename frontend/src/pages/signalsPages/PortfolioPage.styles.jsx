import styled from 'styled-components';

export const PageContainer = styled.div`
    width: 100%;
    max-width: 1400px;
    min-height: 100vh;
    margin: 0 auto;
    padding: 2rem 1.5rem 4rem;

    display: flex;
    flex-direction: column;
    gap: 1.25rem;

    color: #e7edf5;
    background: #0b0f14;

    @media (max-width: 768px) {
        padding: 1.25rem 0.9rem 3rem;
        gap: 1rem;
    }
`;

export const Header = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;

    h2 {
        margin: 0;
        color: #f1f5f9;
        font-size: 1.4rem;
        font-weight: 650;
        letter-spacing: -0.02em;
    }

    @media (max-width: 600px) {
        align-items: flex-start;
        flex-direction: column;
    }
`;

export const BackButton = styled.button`
    display: inline-flex;
    align-items: center;
    justify-content: center;

    padding: 0.6rem 1rem;

    color: #b9c5d3;
    background: #151d27;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 7px;

    font-size: 0.85rem;
    cursor: pointer;

    transition:
        color 0.2s ease,
        background 0.2s ease,
        border-color 0.2s ease;

    &:hover {
        color: #f1f5f9;
        background: #1c2733;
        border-color: rgba(138, 180, 248, 0.45);
    }

    &:focus-visible {
        outline: 2px solid #8ab4f8;
        outline-offset: 2px;
    }
`;

export const StatsGrid = styled.div`
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 0.9rem;

    @media (max-width: 1050px) {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    @media (max-width: 520px) {
        grid-template-columns: 1fr;
    }
`;

export const StatCard = styled.div`
    min-width: 0;
    padding: 1.1rem 1.15rem;

    background: #141b24;
    border: 1px solid rgba(255, 255, 255, 0.075);
    border-radius: 9px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.16);

    transition:
        border-color 0.2s ease,
        transform 0.2s ease;

    &:hover {
        border-color: rgba(138, 180, 248, 0.25);
        transform: translateY(-2px);
    }

    label {
        display: block;
        margin-bottom: 0.5rem;

        overflow: hidden;
        color: #8491a2;
        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.08em;
        line-height: 1.3;
        text-overflow: ellipsis;
        text-transform: uppercase;
        white-space: nowrap;
    }

    value {
        display: block;
        overflow: hidden;

        color: #edf2f7;
        font-size: clamp(1.15rem, 2vw, 1.45rem);
        font-weight: 700;
        line-height: 1.25;
        text-overflow: ellipsis;
        white-space: nowrap;
    }
`;

export const ChartCard = styled.div`
    padding: 1.25rem;

    background: #141b24;
    border: 1px solid rgba(255, 255, 255, 0.075);
    border-radius: 9px;
    box-shadow: 0 10px 28px rgba(0, 0, 0, 0.17);

    h3 {
        margin: 0 0 1rem;

        color: #e7edf5;
        font-size: 1rem;
        font-weight: 600;
        letter-spacing: -0.01em;
    }

    @media (max-width: 600px) {
        padding: 1rem;
    }
`;

export const ChartContainer = styled.div`
    position: relative;
    height: 380px;
    min-width: 0;

    @media (max-width: 700px) {
        height: 300px;
    }

    @media (max-width: 450px) {
        height: 250px;
    }
`;

export const ControlsContainer = styled.div`
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.85rem;
    margin-bottom: 1rem;

    h3 {
        margin: 0;
    }

    @media (max-width: 600px) {
        align-items: flex-start;
        flex-direction: column;
    }
`;

export const LimitGroup = styled.div`
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.35rem;

    color: #8996a7;
    font-size: 0.78rem;

    span {
        margin-right: 0.2rem;
    }
`;

export const LimitButton = styled.button`
    min-width: 38px;
    padding: 0.35rem 0.6rem;

    color: ${({ active }) => (active ? '#07111d' : '#aebaca')};
    background: ${({ active }) => (active ? '#8ab4f8' : '#1a232e')};
    border: 1px solid
        ${({ active }) =>
            active ? '#8ab4f8' : 'rgba(255, 255, 255, 0.1)'};
    border-radius: 5px;

    font-size: 0.72rem;
    cursor: pointer;

    transition:
        color 0.2s ease,
        background 0.2s ease,
        border-color 0.2s ease;

    &:hover {
        color: ${({ active }) => (active ? '#07111d' : '#f1f5f9')};
        background: ${({ active }) => (active ? '#9bc1ff' : '#243140')};
        border-color: #8ab4f8;
    }

    &:focus-visible {
        outline: 2px solid #8ab4f8;
        outline-offset: 2px;
    }
`;

export const TradesTable = styled.div`
    width: 100%;
    overflow-x: auto;
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 7px;

    table {
        width: 100%;
        min-width: 520px;
        border-collapse: collapse;
        font-size: 0.85rem;
    }

    th {
        padding: 0.8rem 0.9rem;

        color: #8d9aab;
        background: #10161e;

        font-size: 0.68rem;
        font-weight: 600;
        letter-spacing: 0.07em;
        text-align: left;
        text-transform: uppercase;
        white-space: nowrap;
    }

    td {
        padding: 0.8rem 0.9rem;

        color: #c5cfdb;
        border-top: 1px solid rgba(255, 255, 255, 0.06);
        white-space: nowrap;
    }

    tbody tr {
        transition: background 0.2s ease;

        &:hover {
            background: rgba(138, 180, 248, 0.045);
        }
    }

    tbody td:nth-child(2) {
        color: #edf2f7;
        font-weight: 600;
    }
`;

export const PaginationContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.3rem;
    margin-top: 1rem;

    span {
        margin-left: 0.7rem;
        color: #7f8b9b;
        font-size: 0.8rem;
    }

    @media (max-width: 600px) {
        span {
            width: 100%;
            margin: 0.4rem 0 0;
            text-align: center;
        }
    }
`;

export const PageButton = styled.button`
    min-width: 34px;
    height: 34px;
    padding: 0 0.45rem;

    color: ${({ active }) => (active ? '#07111d' : '#b4c0ce')};
    background: ${({ active }) => (active ? '#8ab4f8' : '#1a232e')};
    border: 1px solid
        ${({ active }) =>
            active ? '#8ab4f8' : 'rgba(255, 255, 255, 0.1)'};
    border-radius: 5px;

    font-size: 0.78rem;
    cursor: pointer;

    transition:
        color 0.2s ease,
        background 0.2s ease,
        border-color 0.2s ease;

    &:disabled {
        opacity: 0.3;
        cursor: not-allowed;
    }

    &:hover:not(:disabled) {
        color: ${({ active }) => (active ? '#07111d' : '#f1f5f9')};
        background: ${({ active }) => (active ? '#9bc1ff' : '#243140')};
        border-color: #8ab4f8;
    }

    &:focus-visible {
        outline: 2px solid #8ab4f8;
        outline-offset: 2px;
    }
`;

export const LoadingContainer = styled.div`
    padding: 6rem 1rem;

    color: #9aa7b6;
    font-size: 1rem;
    text-align: center;
`;

export const ErrorContainer = styled.div`
    padding: 4rem 1.5rem;

    color: #f87171;
    text-align: center;

    > div:last-child {
        color: #8996a7 !important;
    }
`;

export const EmptyContainer = styled.div`
    display: flex;
    justify-content: center;
    align-items: center;
    height: 100%;

    color: #7f8b9b;
    font-size: 0.9rem;
`;
