// src/pages/signalsPages/TradesPage.jsx
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
    LoadingContainer,
    ErrorContainer,
    TradesTable,
    ChartContainer,
    PaginationContainer,
    PageButton,
    ControlsContainer,
    LimitGroup,
    LimitButton
} from './TradesPage.styles.jsx';

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

function TradesPage() {
    const { signalId } = useParams();
    const navigate = useNavigate();
    
    const [chartData, setChartData] = useState([]);
    const [tableData, setTableData] = useState([]);
    const [strategy, setStrategy] = useState('');
    const [statistics, setStatistics] = useState({ total_trades: 0 });
    const [pagination, setPagination] = useState({
        current_page: 1,
        limit: 50,
        total: 0,
        total_pages: 1
    });
    
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [chartLimit, setChartLimit] = useState(50);
    
    const CHART_LIMITS = [50, 100, 150, 200, -1]; // -1 означает все данные

    const fetchTrades = async (page = 1, limit = 50, chartLimit = 50) => {
        try {
            setLoading(true);
            setError(null);
            
            const response = await axios.get(`${API_BASE}/getTradesBySignal/${signalId}`, {
                params: { 
                    page, 
                    limit, 
                    chart_limit: chartLimit 
                }
            });
            
            // Проверяем, что данные пришли корректно
            if (response.data && typeof response.data === 'object') {
                setChartData(response.data.chart_data || []);
                setTableData(response.data.table_data || []);
                setStrategy(response.data.strategy || '');
                setStatistics(response.data.statistics || { total_trades: 0 });
                setPagination(response.data.pagination || {
                    current_page: 1,
                    limit: 50,
                    total: 0,
                    total_pages: 1
                });
            } else {
                throw new Error('Неверный формат данных');
            }
        } catch (err) {
            console.error('Error fetching trades:', err);
            // Обрабатываем ошибку более детально
            let errorMessage = 'Ошибка загрузки данных';
            if (err.response) {
                // Сервер ответил с ошибкой
                if (err.response.data && typeof err.response.data === 'object') {
                    if (err.response.data.detail) {
                        errorMessage = err.response.data.detail;
                    } else if (err.response.data.message) {
                        errorMessage = err.response.data.message;
                    } else {
                        errorMessage = JSON.stringify(err.response.data);
                    }
                } else {
                    errorMessage = err.response.data || errorMessage;
                }
            } else if (err.request) {
                // Запрос был сделан, но ответа не получено
                errorMessage = 'Сервер не отвечает. Проверьте подключение.';
            } else {
                // Что-то пошло не так при настройке запроса
                errorMessage = err.message || errorMessage;
            }
            setError(errorMessage);
            setChartData([]);
            setTableData([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchTrades(1, 50, chartLimit);
    }, [signalId, chartLimit]);

    const handlePageChange = (newPage) => {
        if (newPage >= 1 && newPage <= pagination.total_pages) {
            fetchTrades(newPage, pagination.limit, chartLimit);
        }
    };

    const handleChartLimitChange = (newLimit) => {
        setChartLimit(newLimit);
    };

    if (loading) {
        return (
            <PageContainer>
                <LoadingContainer>⏳ Загрузка данных...</LoadingContainer>
            </PageContainer>
        );
    }

    if (error) {
        return (
            <PageContainer>
                <ErrorContainer>
                    <div>
                        <div style={{ fontSize: '48px', marginBottom: '12px' }}>❌</div>
                        <div style={{ fontSize: '18px', fontWeight: '600', marginBottom: '8px' }}>
                            Ошибка загрузки
                        </div>
                        <div style={{ fontSize: '14px', color: '#6b7280' }}>
                            {error}
                        </div>
                        <button 
                            onClick={() => fetchTrades(1, 50, chartLimit)}
                            style={{
                                marginTop: '16px',
                                padding: '8px 24px',
                                background: '#8b5cf6',
                                color: 'white',
                                border: 'none',
                                borderRadius: '8px',
                                cursor: 'pointer',
                                fontSize: '14px'
                            }}
                        >
                            Попробовать снова
                        </button>
                    </div>
                </ErrorContainer>
            </PageContainer>
        );
    }

    if (!chartData || chartData.length === 0) {
        return (
            <PageContainer>
                <Header>
                    <h2>📊 График сделок</h2>
                    <BackButton onClick={() => navigate('/signals/analyst')}>← Назад к сигналам</BackButton>
                </Header>
                <ChartCard>
                    <h3>📭 Нет данных по сделкам для этого сигнала</h3>
                </ChartCard>
            </PageContainer>
        );
    }

    // Подготовка данных для графика
    const labels = chartData.map((trade, index) => {
        return `#${index + 1}\n${trade.datetime}`;
    });

    const deposits = chartData.map((trade) => parseFloat(trade.deposit));

    const chartConfig = {
        labels: labels,
        datasets: [
            {
                label: 'Депозит',
                data: deposits,
                borderColor: '#8b5cf6',
                backgroundColor: 'rgba(139, 92, 246, 0.1)',
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#8b5cf6',
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }
        ]
    };

    const chartOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                display: true,
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                }
            },
            tooltip: {
                callbacks: {
                    label: function(context) {
                        return `$${context.parsed.y.toFixed(2)}`;
                    }
                }
            }
        },
        scales: {
            y: {
                ticks: {
                    callback: function(value) {
                        return '$' + value.toFixed(2);
                    }
                }
            },
            x: {
                ticks: {
                    maxRotation: 45,
                    minRotation: 45,
                    font: {
                        size: 10
                    }
                }
            }
        }
    };

    // Статистика
    const firstDeposit = deposits[0];
    const lastDeposit = deposits[deposits.length - 1];
    const depositChange = ((lastDeposit - firstDeposit) / firstDeposit * 100).toFixed(2);
    const maxDeposit = Math.max(...deposits);
    const minDeposit = Math.min(...deposits);

    // Рендер кнопок пагинации
    const renderPaginationButtons = () => {
        const { current_page, total_pages } = pagination;
        const pages = [];
        const maxVisible = 5;
        
        let startPage = Math.max(1, current_page - Math.floor(maxVisible / 2));
        let endPage = Math.min(total_pages, startPage + maxVisible - 1);
        
        if (endPage - startPage < maxVisible - 1) {
            startPage = Math.max(1, endPage - maxVisible + 1);
        }
        
        for (let i = startPage; i <= endPage; i++) {
            pages.push(i);
        }
        
        return (
            <>
                <PageButton 
                    onClick={() => handlePageChange(1)}
                    disabled={current_page === 1}
                >
                    ⟪
                </PageButton>
                <PageButton 
                    onClick={() => handlePageChange(current_page - 1)}
                    disabled={current_page === 1}
                >
                    ⟨
                </PageButton>
                
                {pages.map(page => (
                    <PageButton
                        key={page}
                        active={page === current_page}
                        onClick={() => handlePageChange(page)}
                    >
                        {page}
                    </PageButton>
                ))}
                
                <PageButton 
                    onClick={() => handlePageChange(current_page + 1)}
                    disabled={current_page === total_pages}
                >
                    ⟩
                </PageButton>
                <PageButton 
                    onClick={() => handlePageChange(total_pages)}
                    disabled={current_page === total_pages}
                >
                    ⟫
                </PageButton>
            </>
        );
    };

    return (
        <PageContainer>
            <Header>
                <h2>📊 График сделок для {strategy}</h2>
                <BackButton onClick={() => navigate('/signals/analyst')}>← Назад к сигналам</BackButton>
            </Header>

            <StatsGrid>
                <StatCard>
                    <label>Всего сделок</label>
                    <value>{statistics.total_trades}</value>
                </StatCard>
                <StatCard>
                    <label>Начальный депозит</label>
                    <value>${firstDeposit.toFixed(2)}</value>
                </StatCard>
                <StatCard>
                    <label>Конечный депозит</label>
                    <value>${lastDeposit.toFixed(2)}</value>
                </StatCard>
                <StatCard>
                    <label>Изменение</label>
                    <value style={{ color: depositChange >= 0 ? '#10b981' : '#ef4444' }}>
                        {depositChange >= 0 ? '+' : ''}{depositChange}%
                    </value>
                </StatCard>
                <StatCard>
                    <label>Максимум</label>
                    <value>${maxDeposit.toFixed(2)}</value>
                </StatCard>
                <StatCard>
                    <label>Минимум</label>
                    <value>${minDeposit.toFixed(2)}</value>
                </StatCard>
            </StatsGrid>

            <ChartCard>
                <ControlsContainer>
                    <h3>Динамика депозита по времени</h3>
                    <LimitGroup>
                        <span>Показать:</span>
                        {CHART_LIMITS.map(limit => (
                            <LimitButton
                                key={limit}
                                active={chartLimit === limit}
                                onClick={() => handleChartLimitChange(limit)}
                            >
                                {limit === -1 ? 'Всё' : limit}
                            </LimitButton>
                        ))}
                    </LimitGroup>
                </ControlsContainer>
                <ChartContainer>
                    <Line data={chartConfig} options={chartOptions} />
                </ChartContainer>
            </ChartCard>

            <ChartCard>
                <h3>📋 Список сделок</h3>
                <TradesTable>
                    <table>
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>Депозит</th>
                                <th>Дата</th>
                            </tr>
                        </thead>
                        <tbody>
                            {tableData.length > 0 ? (
                                tableData.map((trade, index) => (
                                    <tr key={trade.id}>
                                        <td>{index + 1 + (pagination.current_page - 1) * pagination.limit}</td>
                                        <td>${trade.deposit}</td>
                                        <td>{trade.datetime}</td>
                                    </tr>
                                ))
                            ) : (
                                <tr>
                                    <td colSpan="3" style={{ textAlign: 'center', padding: '20px', color: '#6b7280' }}>
                                        Нет данных для отображения
                                    </td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </TradesTable>
                
                {pagination.total_pages > 1 && (
                    <PaginationContainer>
                        {renderPaginationButtons()}
                        <span style={{ marginLeft: '16px', color: '#6b7280', fontSize: '14px' }}>
                            Всего: {pagination.total} записей
                        </span>
                    </PaginationContainer>
                )}
            </ChartCard>
        </PageContainer>
    );
}

export default TradesPage;