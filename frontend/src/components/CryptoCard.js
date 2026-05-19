import React from 'react';

function CryptoCard({ data }) {
	return (
		<div className="crypto-card">
			<h3 className="card-title">{data.asset}</h3>
			<table className="crypto-table">
				<tbody>
					<tr>
						<td className="label">Signal</td>
						<td className="label">ML модель</td>
						<td className="label">Таймфрэйм</td>
					</tr>
					<tr>
						<td className={`signal ${data.signal.toLowerCase()}`}>{data.signal}</td>
						<td className="value">{data.ml_model}</td>
						<td className="value">{data.timeframe}</td>
					</tr>
				</tbody>
			</table>
		</div>
	);
}

export default CryptoCard;