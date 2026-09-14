import { useState, useEffect } from 'react';
import CryptoCard from './CryptoCard.jsx';
import {
    CardsPage,
    LoadSection,
    Spinner,
    CardsList
} from './AnalystPage.styles.jsx';

const API_BASE = process.env.REACT_APP_API_URL;

function AnalystPage() {
    const [cards, setCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadCards = async () => {
            try {
                const response = await fetch(`${API_BASE}/getTableAnalyst`);
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                setCards(data);
            } catch (error) {
                console.error('Loading error:', error);
                setError(error.message);
                alert('Failed to load cards');
            } finally {
                setLoading(false);
            }
        };

        loadCards();
    }, []);

    if (loading) {
        return (
            <CardsPage>
                <h1>Analytics</h1>
                <LoadSection>
                    <p>Loading data...</p>
                    <Spinner>⏳</Spinner>
                </LoadSection>
            </CardsPage>
        );
    }

    if (error) {
        return (
            <CardsPage>
                <h1>Analytics</h1>
                <LoadSection>
                    <p>❌ Error: {error}</p>
                    <button onClick={() => window.location.reload()}>
                        Try again
                    </button>
                </LoadSection>
            </CardsPage>
        );
    }

    return (
        <CardsPage>
            <h1>Analytics</h1>
            
            {cards.length === 0 ? (
                <LoadSection>
                    <p>📭 No data to display</p>
                </LoadSection>
            ) : (
                <CardsList>
                    {cards.map(card => (
                        <CryptoCard key={card.id} data={card} />
                    ))}
                </CardsList>
            )}
        </CardsPage>
    );
}

export default AnalystPage;
