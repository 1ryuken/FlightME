
import React, { useState } from 'react';
import { Calendar, MapPin, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { flightService, FlightSearchParams } from '@/services/flightService';
import { toast } from 'sonner';
import { useQueryClient } from '@tanstack/react-query';

const FlightSearch: React.FC = () => {
  const [origin, setOrigin] = useState('');
  const [destination, setDestination] = useState('');
  const [departDate, setDepartDate] = useState('');
  const [returnDate, setReturnDate] = useState('');
  const [passengers, setPassengers] = useState('1');
  const [isSearching, setIsSearching] = useState(false);
  
  const queryClient = useQueryClient();

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!origin || !destination || !departDate || !returnDate) {
      toast.error("Please fill in all required fields");
      return;
    }

    try {
      setIsSearching(true);
      
      const searchParams: FlightSearchParams = {
        origin,
        destination,
        departDate,
        returnDate,
        passengers: parseInt(passengers, 10)
      };
      
      // Call the service method that will eventually connect to the backend
      const result = await flightService.searchFlights(searchParams);
      
      // Update global state with the results (using React Query)
      queryClient.setQueryData(['flightPriceData'], result.data);
      
      // Show success message
      toast.success("Flight prices analyzed successfully!");
      
    } catch (error) {
      console.error("Error during flight search:", error);
      // Error already handled in the service
    } finally {
      setIsSearching(false);
    }
  };

  return (
    <div className="bg-white p-6 rounded-3xl shadow-lg">
      <h2 className="text-2xl font-bold mb-4 text-flight-gray">Find your flight</h2>
      
      <form onSubmit={handleSearch} className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-flight-gray">From</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 h-4 w-4 text-flight-gray" />
              <Input
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="City or Airport"
                className="pl-10 bg-flight-light border-flight-yellow focus:border-flight-orange"
                required
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="block text-sm font-medium text-flight-gray">To</label>
            <div className="relative">
              <MapPin className="absolute left-3 top-3 h-4 w-4 text-flight-gray" />
              <Input
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="City or Airport"
                className="pl-10 bg-flight-light border-flight-yellow focus:border-flight-orange"
                required
              />
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-flight-gray">Depart</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-3 h-4 w-4 text-flight-gray" />
              <Input
                type="date"
                value={departDate}
                onChange={(e) => setDepartDate(e.target.value)}
                className="pl-10 bg-flight-light border-flight-yellow focus:border-flight-orange"
                required
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="block text-sm font-medium text-flight-gray">Return</label>
            <div className="relative">
              <Calendar className="absolute left-3 top-3 h-4 w-4 text-flight-gray" />
              <Input
                type="date"
                value={returnDate}
                onChange={(e) => setReturnDate(e.target.value)}
                className="pl-10 bg-flight-light border-flight-yellow focus:border-flight-orange"
                required
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <label className="block text-sm font-medium text-flight-gray">Passengers</label>
            <div className="relative">
              <Users className="absolute left-3 top-3 h-4 w-4 text-flight-gray" />
              <Select value={passengers} onValueChange={setPassengers}>
                <SelectTrigger className="pl-10 bg-flight-light border-flight-yellow focus:border-flight-orange">
                  <SelectValue placeholder="Passengers" />
                </SelectTrigger>
                <SelectContent>
                  {[1, 2, 3, 4, 5].map((num) => (
                    <SelectItem key={num} value={num.toString()}>{num} {num === 1 ? 'Passenger' : 'Passengers'}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
        </div>

        <Button 
          type="submit" 
          className="w-full bg-flight-yellow hover:bg-flight-orange text-black font-bold py-3 rounded-full transition-all duration-300 transform hover:scale-105"
          disabled={isSearching}
        >
          {isSearching ? 'Analyzing Prices...' : 'Find Best Prices'}
        </Button>
      </form>
    </div>
  );
};

export default FlightSearch;
