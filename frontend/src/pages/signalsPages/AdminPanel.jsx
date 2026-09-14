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
    const { logout, apiKey } = useAuth();
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
            alert(response.data.message || 'Successfully deleted!');
            await loadData();
        } catch (error) {
            console.error('Error deleting:', error);
            alert('Deletion error: ' + (error.response?.data?.detail || error.message));
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
        if (window.confirm('Are you sure you want to log out?')) {
            logout();
            navigate('/signals/login');
        }
    };

    if (loading) {
        return (
            <AdminContainer>
                <LoadingSpinner>
                    <div className="spinner"></div>
                    <p>Loading data...</p>
                </LoadingSpinner>
            </AdminContainer>
        );
    }

    return (
        <AdminContainer>
            <AdminHeader>
                <Title>
                    <span className="icon">📊</span>
                    Admin panel
                </Title>
                <HeaderActions>
                    <RefreshButton onClick={loadData}>
                        🔄 Update
                    </RefreshButton>
                    <LogoutButton onClick={handleLogout}>
                        🚪 Log out
                    </LogoutButton>
                </HeaderActions>
            </AdminHeader>

            <StatsGrid>
                <StatCard>
                    <div className="number">{stats.total_signals || 0}</div>
                    <div className="label">📈 Strategies</div>
                </StatCard>
                <StatCard>
                    <div className="number">{stats.total_trades || 0}</div>
                    <div className="label">🔄 Trades</div>
                </StatCard>
            </StatsGrid>


            <Section>
                <SectionHeader color="#667eea">
                    <h3>📋 Strategies (signals)</h3>
                    <span className="badge">{signals.length}</span>
                </SectionHeader>
                <TableWrapper>
                    {signals.length === 0 ? (
                        <EmptyState>
                            <div className="icon">📭</div>
                            <p>There are no strategies in the database</p>
                        </EmptyState>
                    ) : (
                        <Table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Name</th>
                                    <th>Deposit</th>
                                    <th>Status</th>
                                    <th>Trades</th>
                                    <th>Date</th>
                                    <th>Actions</th>
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
                                                {signal.status === 'active' ? '🟢 Active' : '🔴 Inactive'}
                                            </StatusBadge>
                                        </td>
                                        <td>{signal.trades_count || 0}</td>
                                        <td>{signal.datetime || 'N/A'}</td>
                                        <td>
                                            <DeleteButton onClick={() => confirmDelete(
                                                'signal', 
                                                signal.id, 
                                                signal.strategy,
                                                `Trades: ${signal.trades_count || 0}`
                                            )}>
                                                🗑️ Delete
                                            </DeleteButton>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </Table>
                    )}
                </TableWrapper>
            </Section>


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