import { useState, useEffect } from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import {
  AnalystContainer,
  Title as PageTitle,
  FiltersContainer,
  Select,
  LoadButton,
  ForecastsGrid,
  ForecastCard,
  CardTitle,
  CardInfo,
  CardMape,
  ChartContainer,
  InfoBlock
} from './AnalystPage.styles';

// Регистрируем компоненты Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

const API_BASE = process.env.REACT_APP_API_URL;

function AnalystPage() {
  const [forecasts, setForecasts] = useState([]);
  const [filteredForecasts, setFilteredForecasts] = useState([]);
  const [symbols, setSymbols] = useState([]);
  const [timeframes, setTimeframes] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('');
  const [selectedTimeframe, setSelectedTimeframe] = useState('');
  const [selectedForecast, setSelectedForecast] = useState(null);
  const [chartData, setChartData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Загрузка списка прогнозов
  useEffect(() => {
    loadForecasts();
  }, []);

  const loadForecasts = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${API_BASE}/getForecastsList`);
      const data = await response.json();
      setForecasts(data);
      
      // Уникальные символы и таймфреймы для фильтров
      const uniqueSymbols = [...new Set(data.map(f => f.symbol))];
      const uniqueTimeframes = [...new Set(data.map(f => f.timeframe))];
      setSymbols(uniqueSymbols);
      setTimeframes(uniqueTimeframes);
      
      setFilteredForecasts(data);
    } catch (error) {
      console.error('Ошибка:', error);
    } finally {
      setLoading(false);
    }
  };

  // Применение фильтров
  const handleFilter = () => {
    let filtered = forecasts;
    if (selectedSymbol) {
      filtered = filtered.filter(f => f.symbol === selectedSymbol);
    }
    if (selectedTimeframe) {
      filtered = filtered.filter(f => f.timeframe === selectedTimeframe);
    }
    setFilteredForecasts(filtered);
    setSelectedForecast(null);
    setChartData(null);
  };

  // Загрузка данных прогноза и подготовка для графика
  const loadForecastData = async (forecast) => {
    setSelectedForecast(forecast);
    setLoading(true);
    
    try {
      const response = await fetch(`${API_BASE}/getForecastData/${forecast.id}`);
      const data = await response.json();
      
      // Подготавливаем данные для react-chartjs-2
      const labels = [
        ...data.historical.map(p => {
          const date = new Date(p.timestamp);
          return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          });
        }),
        ...data.prediction.map(p => {
          const date = new Date(p.timestamp);
          return date.toLocaleString('ru-RU', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
          });
        })
      ];
      
      const historicalPrices = [
        ...data.historical.map(p => p.price),
        ...Array(data.prediction.length).fill(null)
      ];
      
      const predictionPrices = [
        ...Array(data.historical.length).fill(null),
        ...data.prediction.map(p => p.price)
      ];
      
      setChartData({
        labels: labels,
        datasets: [
          {
            label: 'Исторические данные',
            data: historicalPrices,
            borderColor: '#FFFFFF', // Белый цвет
            backgroundColor: 'transparent',
            borderWidth: 2,
            pointRadius: 0,
            tension: 0.1,
            fill: false
          },
          {
            label: 'Прогноз',
            data: predictionPrices,
            borderColor: '#9C27B0', // Фиолетовый цвет
            backgroundColor: 'transparent',
            borderWidth: 2,
            borderDash: [5, 5],
            pointRadius: 3,
            pointBackgroundColor: '#9C27B0',
            tension: 0.1,
            fill: false
          }
        ]
      });
      
    } catch (error) {
      console.error('Ошибка загрузки данных:', error);
    } finally {
      setLoading(false);
    }
  };

  // Настройки графика
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    plugins: {
      legend: {
        position: 'top',
        labels: {
          color: '#e0e0e0',
          font: { size: 12 }
        }
      },
      tooltip: {
        callbacks: {
          label: function(context) {
            if (context.raw === null) return '';
            return `${context.dataset.label}: $${context.raw.toFixed(2)}`;
          }
        }
      }
    },
    scales: {
      x: {
        title: {
          display: true,
          text: 'Дата и время',
          color: '#e0e0e0'
        },
        ticks: {
          color: '#e0e0e0',
          maxRotation: 45,
          minRotation: 45
        },
        grid: {
          color: '#2a2e39'
        }
      },
      y: {
        title: {
          display: true,
          text: 'Цена (USD)',
          color: '#e0e0e0'
        },
        ticks: {
          color: '#e0e0e0',
          callback: function(value) {
            return '$' + value.toFixed(2);
          }
        },
        grid: {
          color: '#2a2e39'
        }
      }
    }
  };

  return (
    <AnalystContainer>
      <PageTitle>Аналитика и прогнозы</PageTitle>
      
      {/* Фильтры */}
      <FiltersContainer>
        <Select 
          value={selectedSymbol} 
          onChange={(e) => setSelectedSymbol(e.target.value)}
        >
          <option value="">Все активы</option>
          {symbols.map(symbol => (
            <option key={symbol} value={symbol}>{symbol}</option>
          ))}
        </Select>
        
        <Select 
          value={selectedTimeframe} 
          onChange={(e) => setSelectedTimeframe(e.target.value)}
        >
          <option value="">Все таймфреймы</option>
          {timeframes.map(tf => (
            <option key={tf} value={tf}>{tf}</option>
          ))}
        </Select>
        
        <LoadButton onClick={handleFilter}>
          Применить фильтр
        </LoadButton>
      </FiltersContainer>
      
      {/* Список прогнозов */}
      {loading && <div style={{color: 'white'}}>Загрузка...</div>}
      
      <ForecastsGrid>
        {filteredForecasts.map(forecast => (
          <ForecastCard 
            key={forecast.id}
            $active={selectedForecast?.id === forecast.id}
            onClick={() => loadForecastData(forecast)}
          >
            <CardTitle>{forecast.symbol}</CardTitle>
            <CardInfo>Таймфрейм: {forecast.timeframe}</CardInfo>
            <CardMape>MAPE: {forecast.mape_score?.toFixed(2) || 'N/A'}%</CardMape>
            <CardInfo>ID: {forecast.id}</CardInfo>
          </ForecastCard>
        ))}
      </ForecastsGrid>
      
      {/* График */}
      {chartData && (
        <ChartContainer>
          <InfoBlock>
            <h3>{selectedForecast?.symbol} - {selectedForecast?.timeframe}</h3>
            <p>Точность прогноза (MAPE): {selectedForecast?.mape_score?.toFixed(2)}%</p>
            <p>Точек: {chartData.datasets[0].data.filter(v => v !== null).length} история + {chartData.datasets[1].data.filter(v => v !== null).length} прогноз</p>
          </InfoBlock>
          <Line data={chartData} options={chartOptions} />
        </ChartContainer>
      )}
    </AnalystContainer>
  );
}

export default AnalystPage;
