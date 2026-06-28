import {
    CryptoCardContainer,
    CardTitle,
    CryptoTable,
    Label,
    Value
} from './BacktestCard.styles.jsx';

function BacktestCard({ data }) {
    return (
        <CryptoCardContainer>
            <CardTitle>{data.strategy}</CardTitle>
            <CryptoTable>
                <tbody>
                    <tr>
                        <Label>Year Profit</Label>
                        <Label>Max Drawdown</Label>
                        <Label>Sharp</Label>
                        <Label>Datetime</Label>
                    </tr>
                    <tr>
                        <Value>{data.year_profit}</Value>
                        <Value>{data.max_drawdown}</Value>
                        <Value>{data.sharp}</Value>
                        <Value>{data.datetime}</Value>
                    </tr>
                </tbody>
            </CryptoTable>
        </CryptoCardContainer>
    );
}

export default BacktestCard;