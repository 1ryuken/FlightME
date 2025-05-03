
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceDot } from 'recharts';
import { PriceTrendPoint } from '@/services/flightService';

interface PriceChartProps {
  priceTrends: PriceTrendPoint[];
}

const PriceChart: React.FC<PriceChartProps> = ({ priceTrends }) => {
  // Default data if no trends provided
  const chartData = priceTrends.length > 0 ? priceTrends : [
    { date: '2025-05-01', price: 340, isLowestPrice: false },
    { date: '2025-05-02', price: 320, isLowestPrice: false },
    { date: '2025-05-03', price: 300, isLowestPrice: false },
    { date: '2025-05-04', price: 260, isLowestPrice: true },
    { date: '2025-05-05', price: 280, isLowestPrice: false },
    { date: '2025-05-06', price: 310, isLowestPrice: false },
    { date: '2025-05-07', price: 290, isLowestPrice: false },
  ];

  // Find the lowest price point
  const lowestPricePoint = chartData.find(point => point.isLowestPrice);

  // Format the date to show just the day and return it as a string
  const formatXAxis = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.getDate().toString();
  };

  // Format the price to show just the number
  const formatYAxis = (price: number) => {
    return `$${price}`;
  };

  return (
    <div className="h-48">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 5, left: 0, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis 
            dataKey="date" 
            tickFormatter={formatXAxis} 
            tick={{ fontSize: 12 }} 
          />
          <YAxis 
            tickFormatter={formatYAxis} 
            tick={{ fontSize: 12 }} 
            domain={['dataMin - 20', 'dataMax + 20']} 
          />
          <Tooltip 
            formatter={(value) => [`$${value}`, 'Price']} 
            labelFormatter={(label) => {
              const date = new Date(label);
              return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
            }}
          />
          <Line 
            type="monotone" 
            dataKey="price" 
            stroke="#4FC3F7" 
            strokeWidth={2} 
            dot={{ r: 3 }}
            activeDot={{ r: 5 }} 
          />
          
          {lowestPricePoint && (
            <ReferenceDot 
              x={lowestPricePoint.date} 
              y={lowestPricePoint.price} 
              r={6}
              fill="#4CAF50" 
              stroke="none" 
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default PriceChart;
