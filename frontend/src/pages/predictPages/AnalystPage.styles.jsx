import styled from 'styled-components';

export const AnalystContainer = styled.div`
  padding: 20px;
  background: #1a1a2e;
  min-height: 100vh;
  color: #e0e0e0;
`;

export const Title = styled.h1`
  text-align: center;
  margin-bottom: 30px;
  color: #00d4ff;
  font-size: 28px;
`;

export const FiltersContainer = styled.div`
  display: flex;
  gap: 15px;
  justify-content: center;
  margin-bottom: 30px;
  flex-wrap: wrap;
`;

export const Select = styled.select`
  padding: 10px 20px;
  background: #0f3460;
  color: #e0e0e0;
  border: 1px solid #00d4ff;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  
  &:hover {
    background: #16213e;
  }
`;

export const LoadButton = styled.button`
  padding: 10px 25px;
  background: #00d4ff;
  color: #1a1a2e;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-weight: bold;
  font-size: 14px;
  transition: all 0.3s;
  
  &:hover {
    background: #00b8e6;
    transform: translateY(-2px);
  }
`;

export const ForecastsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 30px;
  max-height: 400px;
  overflow-y: auto;
  padding: 10px;
`;

export const ForecastCard = styled.div`
  background: ${props => props.$active ? '#00d4ff20' : '#0f3460'};
  border: 2px solid ${props => props.$active ? '#00d4ff' : 'transparent'};
  border-radius: 10px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.3s;
  
  &:hover {
    transform: translateY(-3px);
    background: #16213e;
  }
`;

export const CardTitle = styled.h3`
  margin: 0 0 10px 0;
  color: #00d4ff;
  font-size: 18px;
`;

export const CardInfo = styled.div`
  font-size: 12px;
  margin: 5px 0;
  color: #b0b0b0;
`;

export const CardMape = styled.div`
  font-size: 14px;
  margin: 8px 0;
  color: #ff6b6b;
  font-weight: bold;
`;

export const ChartContainer = styled.div`
  background: #0f3460;
  border-radius: 10px;
  padding: 20px;
  margin-top: 20px;
`;

export const InfoBlock = styled.div`
  background: #16213e;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
  
  h3 {
    margin: 0 0 10px 0;
    color: #00d4ff;
  }
  
  p {
    margin: 5px 0;
    font-size: 14px;
  }
`;