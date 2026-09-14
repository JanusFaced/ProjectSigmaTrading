import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import {
    PageContainer,
    Header,
    BackButton,
    StatsGrid,
    StatCard,
    ChartCard,
    ChartContainer,
    ControlsContainer,
    LimitGroup,
    LimitButton,
    TradesTable,
    PaginationContainer,
    PageButton,
    LoadingContainer,
    ErrorContainer,
    EmptyContainer
} from './PortfolioPage.styles.jsx';

const API_BASE = process.env.REACT_APP_API_URL;

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
    Filler
);

const CHART_LIMITS = [50, 100, 150, 200, -1];

function PortfolioPage() {
    const navigate = useNavigate();

    const [portfolio, setPortfolio] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [chartData, setChartData] = useState([]);
    const [tableData, setTableData] = useState([]);
    const [statistics, setStatistics] = useState({ total_days: 0 });
    const [pagination, setPagination] = useState({
        current_page: 1,
        limit: 50,
        total: 0,
        total_pages: 1
    });
    const [chartLimit, setChartLimit] = useState(50);


    const fetchHistory = useCallback(async (id, page = 1, limit = 50, cLimit = 50) => {
        try {
            const res = await axios.get(`${API_BASE}/getHistoryPortfolio/${id}`, {
                params: { page, limit, chart_limit: cLimit }
            });
            const d = res.data || {};
            setChartData(d.chart_data || []);
            setTableData(d.table_data || []);
            setStatistics(d.statistics || { total_days: 0 });
            setPagination(d.pagination || {
                current_page: 1, limit: 50, total: 0, total_pages: 1
            });
        } catch (err) {
            console.error('Error fetching history:', err);
            setError(err.response?.data?.error || err.message || 'Error fetching history');
        }
    }, []);


    useEffect(() => {
        let cancelled = false;
        (async () => {
            try {
                setLoading(true);
                setError(null);
                const res = await axios.get(`${API_BASE}/getPortfolio`);
                if (cancelled) return;

                const p = res.data;
                if (!p || !p.id) {
                    throw new Error('Portfolio not found');
                }
                setPortfolio(p);
                await fetchHistory(p.id, 1, 50, chartLimit);
            } catch (err) {
                if (cancelled) return;
                console.error('Error fetching portfolio:', err);
                setError(err.response?.data?.error || err.message || 'Error fetching portfolio');
            } finally {
                if (!cancelled) setLoading(false);
            }
        })();
        return () => { cancelled = true; };
        // eslint-disable-next-line
    }, []);


    useEffect(() => {
        if (!portfolio) return;
        fetchHistory(portfolio.id, 1, 50, chartLimit);
    }, [chartLimit, portfolio, fetchHistory]);

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= pagination.total_pages && portfolio) {
            fetchHistory(portfolio.id, newPage, pagination.limit, chartLimit);
        }
    };


    const chartLabels = chartData.map((t, i) => `#${i + 1}\n${t.datetime}`);
    const chartValues = chartData.map((t) => parseFloat(t.portfolio));

    const chartConfig = {
        labels: chartLabels,
        datasets: [
            {
                label: 'Portfolio',
                data: chartValues,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#8b5cf6',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 3,
                pointHoverRadius: 6,
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: true, position: 'top' },
            tooltip: {
                callbacks: {
                    label: (ctx) => `$${ctx.parsed.y.toFixed(2)}`
                }
            }
        },
        scales: {
            y: {
                ticks: { callback: (v) => '$' + Number(v).toFixed(2) }
            },
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 45,
                    font: { size: 10 }
                }
            }
        }
    };

    const renderPaginationButtons = () => {
        const { current_page, total_pages } = pagination;
        const pages = [];
        const maxVisible = 5;
        let startPage = Math.max(1, current_page - Math.floor(maxVisible / 2));
        let endPage = Math.min(total_pages, startPage + maxVisible - 1);
        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }
        for (let i = startPage; i <= endPage; i++) pages.push(i);

        return (
            <>
                <PageButton onClick={() => handlePageChange(1)} disabled={current_page === 1}>⟪</PageButton>
                <PageButton onClick={() => handlePageChange(current_page - 1)} disabled={current_page === 1}>⟨</PageButton>
                {pages.map(p => (
                    <PageButton key={p} active={p === current_page} onClick={() => handlePageChange(p)}>
                        {p}
                    </PageButton>
                ))}
                <PageButton onClick={() => handlePageChange(current_page + 1)} disabled={current_page === total_pages}>⟩</PageButton>
                <PageButton onClick={() => handlePageChange(total_pages)} disabled={current_page === total_pages}>⟫</PageButton>
            </>
        );
    };


    if (loading) {
        return (
            <PageContainer>
                <LoadingContainer>⏳ Загрузка портфеля...</LoadingContainer>
            </PageContainer>
        );
    }

    if (error || !portfolio) {
        return (
            <PageContainer>
                <ErrorContainer>
                    <div style={{ fontSize: 48, marginBottom: 12 }}>❌</div>
                    <div style={{ fontSize: 18, fontWeight: 600, marginBottom: 8 }}>
                        Ошибка загрузки
                    </div>
                    <div style={{ fontSize: 14, color: '#6b7280' }}>
                        {error || 'portfolio not found'}
                    </div>
                </ErrorContainer>
            </PageContainer>
        );
    }

    const fp = parseFloat(portfolio.full_profit) || 0;
    const yp = parseFloat(portfolio.year_profit) || 0;

    return (
        <PageContainer>
            <StatsGrid>
                <StatCard>
                    <label>Current portfolio</label>
                    <value>${portfolio.portfolio}</value>
                </StatCard>
                <StatCard>
                    <label>Full profit</label>
                    <value style={{ color: fp >= 0 ? '#10b981' : '#ef4444' }}>
                        {fp >= 0 ? '+' : ''}{portfolio.full_profit}
                    </value>
                </StatCard>
                <StatCard>
                    <label>Year profit</label>
                    <value style={{ color: yp >= 0 ? '#10b981' : '#ef4444' }}>
                        {yp >= 0 ? '+' : ''}{portfolio.year_profit}%
                    </value>
                </StatCard>
                <StatCard>
                    <label>Max drawdown</label>
                    <value style={{ color: '#ef4444' }}>{portfolio.max_drawdown}%</value>
                </StatCard>
                <StatCard>
                    <label>Sharpe</label>
                    <value>{portfolio.sharp}</value>
                </StatCard>
                <StatCard>
                    <label>Profit Factor</label>
                    <value>{portfolio.profit_factor}</value>
                </StatCard>
                <StatCard>
                    <label>Days in history</label>
                    <value>{statistics.total_days}</value>
                </StatCard>
                <StatCard>
                    <label>Updated</label>
                    <value style={{ fontSize: 16 }}>{portfolio.datetime}</value>
                </StatCard>
            </StatsGrid>

            <ChartCard>
                <ControlsContainer>
                    <h3>📈 Portfolio performance</h3>
                    <LimitGroup>
                        <span>Show:</span>
                        {CHART_LIMITS.map(limit => (
                            <LimitButton
                                key={limit}
                                active={chartLimit === limit}
                                onClick={() => setChartLimit(limit)}
                            >
                                {limit === -1 ? 'All' : limit}
                            </LimitButton>
                        ))}
                    </LimitGroup>
                </ControlsContainer>
                <ChartContainer>
                    {chartData.length > 0 ? (
                        <Line data={chartConfig} options={chartOptions} />
                    ) : (
                        <EmptyContainer>No data for the chart</EmptyContainer>
                    )}
                </ChartContainer>
            </ChartCard>

            <ChartCard>
                <h3>📋 Change history</h3>
                <TradesTable>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Portfolio</th>
                                <th>Datetime</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tableData.length > 0 ? (
                                tableData.map((row, index) => (
                                    <tr key={row.id}>
                                        <td>
                                            {index + 1 + (pagination.current_page - 1) * pagination.limit}
                                        </td>
                                        <td>${row.portfolio}</td>
                                        <td>{row.datetime}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3" style={{ textAlign: 'center', padding: 20, color: '#6b7280' }}>
                                        No data
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </TradesTable>

                {pagination.total_pages > 1 && (
                    <PaginationContainer>
                        {renderPaginationButtons()}
                        <span style={{ marginLeft: 16, color: '#6b7280', fontSize: 14 }}>
                            Total: {pagination.total} records
                        </span>
                    </PaginationContainer>
                )}
            </ChartCard>
        </PageContainer>
    );
}

export default PortfolioPage;