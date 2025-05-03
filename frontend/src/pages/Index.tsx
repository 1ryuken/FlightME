
import React from 'react';
import Header from '@/components/Header';
import FlightSearch from '@/components/FlightSearch';
import PriceAnalysis from '@/components/PriceAnalysis';
import FlightMascot from '@/components/FlightMascot';
import cloudSvg from '@/assets/cloud.svg';
import sunSvg from '@/assets/sun.svg';

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      {/* Background decorative elements */}
      <div className="fixed top-20 right-20 w-24 h-24 opacity-70 z-0">
        <img src={sunSvg} alt="Sun" className="w-full h-full animate-float" />
      </div>
      <div className="fixed top-40 left-20 w-32 h-16 opacity-70 z-0">
        <img src={cloudSvg} alt="Cloud" className="w-full h-full animate-float" />
      </div>
      <div className="fixed bottom-40 right-40 w-40 h-20 opacity-70 z-0">
        <img src={cloudSvg} alt="Cloud" className="w-full h-full animate-float" />
      </div>
      
      {/* App content */}
      <Header />
      
      <main className="flex-grow container mx-auto px-4 py-8 z-10">
        <div className="flex flex-col lg:flex-row gap-8">
          {/* Left Column */}
          <div className="flex-1">
            <div className="mb-8 flex items-center justify-between">
              <h2 className="text-2xl font-bold text-flight-gray">Find your best deal!</h2>
              <FlightMascot message="Let me analyze flight prices for you!" />
            </div>
            <FlightSearch />
          </div>
          
          {/* Right Column */}
          <div className="flex-1">
            <PriceAnalysis />
          </div>
        </div>
        
        {/* Features highlight */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              icon: "🔍",
              title: "Smart Price Analysis",
              description: "Our AI analyzes millions of flight prices to find patterns and predict the best time to book."
            },
            {
              icon: "⏰",
              title: "Price Alerts",
              description: "Get notified when prices drop or it's the best time to book your desired route."
            },
            {
              icon: "💰",
              title: "Savings Guarantee",
              description: "On average, our users save 23% on flight costs by booking at the optimal time."
            }
          ].map((feature, index) => (
            <div key={index} className="bg-white p-6 rounded-3xl shadow-md hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">{feature.icon}</div>
              <h3 className="text-xl font-bold text-flight-gray mb-2">{feature.title}</h3>
              <p className="text-flight-gray">{feature.description}</p>
            </div>
          ))}
        </div>

        {/* Bottom mascot with message */}
        <div className="mt-12 flex justify-center">
          <FlightMascot message="Ready for takeoff? Let's find your perfect flight deal!" />
        </div>
      </main>
      
      <footer className="mt-auto bg-flight-yellow py-4 text-center">
        <p className="text-flight-gray font-medium">
          © 2025 FlightME - Find your best flight with AI-powered insights! 🚀
        </p>
      </footer>
    </div>
  );
};

export default Index;
