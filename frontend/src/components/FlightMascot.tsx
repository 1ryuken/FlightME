
import React from 'react';
import planeSvg from '../assets/plane.svg';

interface FlightMascotProps {
  message?: string;
}

const FlightMascot: React.FC<FlightMascotProps> = ({ message = "Ready to find your best flight deal!" }) => {
  return (
    <div className="flex items-center">
      <div className="relative">
        <img src={planeSvg} alt="Flight Mascot" className="w-20 h-20 animate-float" />
        {message && (
          <div className="absolute -top-16 left-10 max-w-xs">
            {/* Cloud-shaped message bubble with anime/cartoon style */}
            <div className="relative">
              {/* Main cloud shape */}
              <div className="bg-cloud-white p-4 rounded-3xl border-2 border-flight-blue shadow-lg relative z-10
                            before:content-[''] before:absolute before:w-8 before:h-8 before:bg-cloud-white before:rounded-full before:-bottom-3 before:left-6 before:border-2 before:border-flight-blue before:z-0
                            after:content-[''] after:absolute after:w-5 after:h-5 after:bg-cloud-white after:rounded-full after:-bottom-6 after:left-12 after:border-2 after:border-flight-blue after:z-0">
                <div className="text-sm font-comic font-bold text-flight-gray leading-5">
                  {message}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FlightMascot;
