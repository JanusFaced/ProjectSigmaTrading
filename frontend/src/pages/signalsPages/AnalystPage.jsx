import { useState, useEffect } from 'react';
import CryptoCard from './CryptoCard.jsx';
import {
    CardsPage,
    LoadSection,
    Spinner,
    CardsList
} from './AnalystPage.styles.jsx';

function AnalystPage() {
    const [cards, setCards] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        const loadCards = async () => {
            try {
                const response = await fetch('http://localhost:8000/getTableAnalyst');
                
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                
                const data = await response.json();
                setCards(data);
            } catch (error) {
                console.error('Ошибка загрузки:', error);
                setError(error.message);
                alert('Не удалось загрузить карточки');
            } finally {
                setLoading(false);
            }
        };

        loadCards();
    }, []);

    if (loading) {
        return (
            <CardsPage>
                <h1>Аналитика</h1>
                <LoadSection>
                    <p>Загрузка данных...</p>
                    <Spinner>⏳</Spinner>
                </LoadSection>
            </CardsPage>
        );
    }

    if (error) {
        return (
            <CardsPage>
                <h1>Аналитика</h1>
                <LoadSection>
                    <p>❌ Ошибка: {error}</p>
                    <button onClick={() => window.location.reload()}>
                        Попробовать снова
                    </button>
                </LoadSection>
            </CardsPage>
        );
    }

    return (
        <CardsPage>
            <h1>Аналитика</h1>
            
            {cards.length === 0 ? (
                <LoadSection>
                    <p>📭 Нет данных для отображения</p>
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