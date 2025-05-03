
// This file will handle all API calls related to flight data
import { toast } from "sonner";

// Types for flight search parameters
export interface FlightSearchParams {
  origin: string;
  destination: string;
  departDate: string;
  returnDate: string;
  passengers: number;
}

// Types for price trend data
export interface PriceTrendPoint {
  date: string;
  price: number;
  isLowestPrice: boolean;
}

export interface PriceInsight {
  icon: string;
  title: string;
  description: string;
  type: 'good' | 'warning' | 'info';
}

// Mock API response while backend is being developed
const getMockPriceTrends = (): PriceTrendPoint[] => {
  const today = new Date();
  return Array.from({ length: 14 }, (_, i) => {
    const date = new Date(today);
    date.setDate(today.getDate() + i);
    
    // Generate some random price data
    let basePrice = 280;
    if (i % 3 === 0) basePrice -= 20;
    if (i % 7 === 0) basePrice -= 30;
    const price = basePrice + Math.floor(Math.random() * 50);
    
    return {
      date: date.toISOString().split('T')[0],
      price,
      isLowestPrice: i === 3 // Mark a specific day as lowest price
    };
  });
};

const getMockInsights = (): PriceInsight[] => {
  return [
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
};

// Flight service for API interactions
class FlightService {
  // This will be replaced with actual API calls
  async searchFlights(params: FlightSearchParams) {
    try {
      console.log("Searching flights with params:", params);
      
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Return mock data
      return {
        success: true,
        message: "Flight search successful",
        data: {
          priceTrends: getMockPriceTrends(),
          insights: getMockInsights()
        }
      };
    } catch (error) {
      console.error("Error searching flights:", error);
      toast.error("Failed to search flights. Please try again.");
      throw error;
    }
  }

  // Additional methods for other API calls can be added here
}

export const flightService = new FlightService();
