import React from 'react';
import { useNavigate } from 'react-router-dom';
import {
	CryptoCardContainer,
	CardTitle,
	CryptoTable,
	Label,
	Value,
	LongSignal,
	ShortSignal,
	LongSignalIndicator,
	ShortSignalIndicator,
	ViewButton,
	ActionCell
} from './CryptoCard.styles.jsx';

function CryptoCard({ data }) {
	const navigate = useNavigate();
	
	const getSignalProps = (signal) => {
		if (!signal) return { type: 'unknown', state: 'unknown' };
		const [type, state] = signal.toLowerCase().split('_');
		return { type, state };
	};

	const longProps = getSignalProps(data.long_signal);
	const shortProps = getSignalProps(data.short_signal);

	const handleViewTrades = () => {
		navigate(`/signals/trades/${data.id}`);
	};

	return (
		<CryptoCardContainer>
			<CardTitle>{data.strategy}</CardTitle>
			<CryptoTable>
				<tbody>
					<tr>
						<Label>Long signal</Label>
						<Label>Short signal</Label>
						<Label>Datetime</Label>
					</tr>
					<tr>
						<LongSignal 
							$signalType={longProps.type}
							$signalState={longProps.state}
						>
							<LongSignalIndicator 
								$signalType={longProps.type}
								$signalState={longProps.state}
							/>
							{data.long_signal || 'N/A'}
						</LongSignal>
						<ShortSignal 
							$signalType={shortProps.type}
							$signalState={shortProps.state}
						>
							<ShortSignalIndicator 
								$signalType={shortProps.type}
								$signalState={shortProps.state}
							/>
							{data.short_signal || 'N/A'}
						</ShortSignal>
						<Value>{data.datetime}</Value>
					</tr>
					<tr>
						<Label>Fiat</Label>
						<Label>Active</Label>
						<Label>Deposit</Label>
					</tr>
					<tr>
						<Value>{data.fiat}</Value>
						<Value>{data.active}</Value>
						<Value>{data.deposit}</Value>
					</tr>
					<tr>
						<Label>Mode</Label>
						<Label>Status</Label>
						<Label>Actions</Label>
					</tr>
					<tr>
						<Value>{data.mode}</Value>
						<Value>{data.status}</Value>
						<ActionCell>
							<ViewButton onClick={handleViewTrades}>
								📊 Open chart!
							</ViewButton>
						</ActionCell>
					</tr>
				</tbody>
			</CryptoTable>
		</CryptoCardContainer>
	);
}

export default CryptoCard;