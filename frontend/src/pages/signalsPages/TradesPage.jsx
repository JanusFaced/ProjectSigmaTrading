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
    ChartContainer
} from './TradesPage.styles.jsx';

const API_BASE = process.env.REACT_APP_API_URL;

// Регистрируем компоненты Chart.js
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
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const fetchTrades = async () => {
            try {
                setLoading(true);
                const response = await axios.get(`${API_BASE}/getTradesBySignal/${signalId}`);
                setData(response.data);
            } catch (err) {
                setError(err.response?.data?.detail || err.message);
            } finally {
                setLoading(false);
            }
        };

        fetchTrades();
    }, [signalId]);

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
                <ErrorContainer>❌ Ошибка: {error}</ErrorContainer>
            </PageContainer>
        );
    }

    if (!data || !data.trades || data.trades.length === 0) {
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
    const labels = data.trades.map((trade, index) => {
        return `#${index + 1}\n${trade.datetime}`;
    });

    const deposits = data.trades.map((trade) => parseFloat(trade.deposit));

    // Данные для графика
    const chartData = {
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

    // Опции графика
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

    return (
        <PageContainer>
            <Header>
                <h2>📊 График сделок для {data.strategy}</h2>
                <BackButton onClick={() => navigate('/signals/analyst')}>← Назад к сигналам</BackButton>
            </Header>

            <StatsGrid>
                <StatCard>
                    <label>Всего сделок</label>
                    <value>{data.statistics.total_trades}</value>
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
                <h3>Динамика депозита по времени</h3>
                <ChartContainer>
                    <Line data={chartData} options={chartOptions} />
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
                            {data.trades.map((trade, index) => (
                                <tr key={trade.id}>
                                    <td>{index + 1}</td>
                                    <td>${trade.deposit}</td>
                                    <td>{trade.datetime}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </TradesTable>
            </ChartCard>
        </PageContainer>
    );
}

export default TradesPage;