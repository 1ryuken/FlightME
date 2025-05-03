
import React from 'react';
import planeSvg from '../assets/plane.svg';

const Header: React.FC = () => {
  return (
    <header className="bg-flight-yellow py-4 px-6 rounded-b-3xl shadow-md">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex items-center gap-3">
          <img src={planeSvg} alt="FlightME Logo" className="w-10 h-10 animate-wiggle" />
          <h1 className="text-3xl font-bold text-white">Flight<span className="text-flight-blue">ME</span></h1>
        </div>
        <div className="text-sm md:text-base font-semibold bg-white px-4 py-2 rounded-full shadow-md text-flight-gray">
          Flight Price Analyzer
        </div>
      </div>
    </header>
  );
};

export default Header;
