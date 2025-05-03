
import React from 'react';
import PriceChart from './PriceChart';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { useQuery } from '@tanstack/react-query';
import { PriceInsight, PriceTrendPoint } from '@/services/flightService';

// Define the type for the price data
interface PriceData {
  insights: PriceInsight[];
  priceTrends: PriceTrendPoint[];
}

const PriceAnalysis: React.FC = () => {
  // Get price data from React Query (that will be populated by FlightSearch)
  const { data: priceData } = useQuery<PriceData>({
    queryKey: ['flightPriceData'],
    enabled: false, // This query doesn't run automatically, it's populated from the search
  });
  
  // Properly type the data from the query
  const insights: PriceInsight[] = priceData?.insights || [
    // Default insights before search
    {
      icon: '💸',
      title: 'Lowest Price',
      description: 'Book on Saturday for the best deal at $260!',
      type: 'good'
    },
    {
      icon: '⚠️',
      title: 'Price Trend',
      description: 'Prices are expected to increase by 15% next week.',
      type: 'warning'
    },
    {
      icon: '🔮',
      title: 'Future Prediction',
      description: 'Wait 3 days for a potential price drop.',
      type: 'info'
    }
  ];
  
  const priceTrends = priceData?.priceTrends || [];

  return (
    <Card className="bg-white rounded-3xl shadow-lg overflow-hidden">
      <CardHeader className="bg-flight-blue bg-opacity-10 pb-2">
        <CardTitle className="text-xl font-bold text-flight-gray flex items-center">
          <span className="mr-2">🧠</span> AI Price Analysis
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4">
        <div className="mb-6">
          <h3 className="text-lg font-semibold text-flight-gray mb-2">Price Trends</h3>
          <PriceChart priceTrends={priceTrends} />
          <div className="text-center text-sm text-flight-gray mt-1">
            Next 14 days forecast
          </div>
        </div>

        <div className="space-y-4">
          <h3 className="text-lg font-semibold text-flight-gray">Price Insights</h3>
          
          {insights.map((insight, index) => (
            <div key={index} className="flex items-start p-3 bg-flight-light rounded-xl">
              <div className="text-2xl mr-3">{insight.icon}</div>
              <div className="flex-grow">
                <div className="flex items-center justify-between">
                  <h4 className="font-semibold text-flight-gray">{insight.title}</h4>
                  <Badge 
                    className={
                      insight.type === 'good' ? 'bg-green-100 text-green-800 hover:bg-green-200' :
                      insight.type === 'warning' ? 'bg-amber-100 text-amber-800 hover:bg-amber-200' :
                      'bg-blue-100 text-blue-800 hover:bg-blue-200'
                    }
                  >
                    {insight.type === 'good' ? 'Good Deal' :
                     insight.type === 'warning' ? 'Act Soon' : 
                     'AI Prediction'}
                  </Badge>
                </div>
                <p className="text-sm text-flight-gray mt-1">{insight.description}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

export default PriceAnalysis;
