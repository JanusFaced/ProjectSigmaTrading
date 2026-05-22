import {
    CryptoCardContainer,
    CardTitle,
    CryptoTable,
    Label,
    Value,
    Signal,
    SignalIndicator
} from './CryptoCard.styles.jsx';

function CryptoCard({ data }) {
    // Приводим сигнал к нижнему регистру для определения цвета
    const signalType = data.signal ? data.signal.toLowerCase() : 'unknown';
    
    return (
        <CryptoCardContainer>
            <CardTitle>{data.asset}</CardTitle>
            <CryptoTable>
                <tbody>
                    <tr>
                        <Label>Signal</Label>
                        <Label>ML модель</Label>
                        <Label>Таймфрэйм</Label>
                    </tr>
                    <tr>
                        <Signal $signalType={signalType}>
                            <SignalIndicator $signalType={signalType} />
                            {data.signal}
                        </Signal>
                        <Value>{data.ml_model}</Value>
                        <Value>{data.timeframe}</Value>
                    </tr>
                </tbody>
            </CryptoTable>
        </CryptoCardContainer>
    );
}

export default CryptoCard;