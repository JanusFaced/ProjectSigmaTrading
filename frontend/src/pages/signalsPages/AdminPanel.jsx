import React, { useState, useEffect } from 'react';
import { useAuth } from './AuthContext.jsx';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import DeleteModal from './DeleteModal';
import { 
    AdminContainer,
    AdminHeader,
    Title,
    HeaderActions,
    Button,
    RefreshButton,
    LogoutButton,
    StatsGrid,
    StatCard,
    Section,
    SectionHeader,
    TableWrapper,
    Table,
    StatusBadge,
    DeleteButton,
    LoadingSpinner,
    EmptyState,
} from './AdminPanel.styles.jsx';

const API_BASE = process.env.REACT_APP_API_URL;

const AdminPanel = () => {
    const { logout, apiKey } = useAuth(); // 👈 ДОБАВЛЯЕМ apiKey
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [stats, setStats] = useState({ total_signals: 0, total_backtests: 0, total_trades: 0 });
    const [signals, setSignals] = useState([]);
    const [deleteModal, setDeleteModal] = useState({ show: false, type: null, id: null, name: '', details: '' });

    const loadData = async () => {
        setLoading(true);
        try {
            const headers = {
                'X-API-Key': apiKey
            };

            const [statsRes] = await Promise.all([
                axios.get(`${API_BASE}/admin/statistics`, { headers })
            ]);
            
            setStats(statsRes.data);
            setSignals(statsRes.data.signals || []);
        } catch (error) {
            console.error('Error loading admin data:', error);
            if (error.response?.status === 403 || error.response?.status === 422) {
                logout();
                navigate('/signals/login');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadData();
    }, []);

    const handleDelete = async (type, id) => {
        try {
            const endpoint = type === 'signal' 
                ? `${API_BASE}/admin/delete-signal/${id}`
                : `${API_BASE}/admin/delete-backtest/${id}`;
            
            const headers = {
                'X-API-Key': apiKey
            };
            
            const response = await axios.delete(endpoint, { headers });
            
            setDeleteModal({ show: false, type: null, id: null, name: '', details: '' });
            alert(response.data.message || 'Успешно удалено!');
            await loadData();
        } catch (error) {
            console.error('Error deleting:', error);
            alert('Ошибка удаления: ' + (error.response?.data?.detail || error.message));
        }
    };

    const confirmDelete = (type, id, name, extraInfo) => {
        let details = `ID: ${id}`;
        if (extraInfo) {
            details += ` | ${extraInfo}`;
        }
        setDeleteModal({
            show: true,
            type,
            id,
            name,
            details
        });
    };

    const handleLogout = () => {
        if (window.confirm('Вы уверены, что хотите выйти?')) {
            logout();
            navigate('/signals/login');
        }
    };

    if (loading) {
        return (
            <AdminContainer>
                <LoadingSpinner>
                    <div className="spinner"></div>
                    <p>Загрузка данных...</p>
                </LoadingSpinner>
            </AdminContainer>
        );
    }

    return (
        <AdminContainer>
            <AdminHeader>
                <Title>
                    <span className="icon">📊</span>
                    Админ-панель
                </Title>
                <HeaderActions>
                    <RefreshButton onClick={loadData}>
                        🔄 Обновить
                    </RefreshButton>
                    <LogoutButton onClick={handleLogout}>
                        🚪 Выйти
                    </LogoutButton>
                </HeaderActions>
            </AdminHeader>

            <StatsGrid>
                <StatCard>
                    <div className="number">{stats.total_signals || 0}</div>
                    <div className="label">📈 Стратегий</div>
                </StatCard>
                <StatCard>
                    <div className="number">{stats.total_trades || 0}</div>
                    <div className="label">🔄 Трейдов</div>
                </StatCard>
            </StatsGrid>

            {/* Стратегии */}
            <Section>
                <SectionHeader color="#667eea">
                    <h3>📋 Стратегии (сигналы)</h3>
                    <span className="badge">{signals.length}</span>
                </SectionHeader>
                <TableWrapper>
                    {signals.length === 0 ? (
                        <EmptyState>
                            <div className="icon">📭</div>
                            <p>Нет стратегий в базе данных</p>
                        </EmptyState>
                    ) : (
                        <Table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Название</th>
                                    <th>Депозит</th>
                                    <th>Статус</th>
                                    <th>Трейдов</th>
                                    <th>Дата</th>
                                    <th>Действия</th>
                                </tr>
                            </thead>
                            <tbody>
                                {signals.map(signal => (
                                    <tr key={signal.id}>
                                        <td><strong>#{signal.id}</strong></td>
                                        <td><strong>{signal.strategy}</strong></td>
                                        <td>${signal.deposit ? parseFloat(signal.deposit).toFixed(2) : '0.00'}</td>
                                        <td>
                                            <StatusBadge active={signal.status === 'active'}>
                                                {signal.status === 'active' ? '🟢 Активна' : '🔴 Неактивна'}
                                            </StatusBadge>
                                        </td>
                                        <td>{signal.trades_count || 0}</td>
                                        <td>{signal.datetime || 'N/A'}</td>
                                        <td>
                                            <DeleteButton onClick={() => confirmDelete(
                                                'signal', 
                                                signal.id, 
                                                signal.strategy,
                                                `Трейдов: ${signal.trades_count || 0}`
                                            )}>
                                                🗑️ Удалить
                                            </DeleteButton>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    )}
                </TableWrapper>
            </Section>

            {/* Модалка подтверждения */}
            <DeleteModal
                show={deleteModal.show}
                onClose={() => setDeleteModal({ show: false, type: null, id: null, name: '', details: '' })}
                onConfirm={() => handleDelete(deleteModal.type, deleteModal.id)}
                name={deleteModal.name}
                details={deleteModal.details}
                type={deleteModal.type}
            />
        </AdminContainer>
    );
};

export default AdminPanel;