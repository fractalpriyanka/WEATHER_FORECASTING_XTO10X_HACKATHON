'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import { FiSearch, FiSun, FiCloud, FiCloudRain, FiWind, FiDroplet, FiMenu, FiX } from 'react-icons/fi';

type WeatherData = {
  name: string;
  main: { temp: number; humidity: number };
  weather: { main: string; description: string }[];
  wind: { speed: number };
};

type ForecastData = {
  [date: string]: {
    temperature: number;
    precipitation: number;
    humidity: number;
    condition: 'sunny' | 'cloudy' | 'raining';
  };
};

export default function Home() {
  const [location, setLocation] = useState('Delhi');
  const [currentWeather, setCurrentWeather] = useState<WeatherData | null>(null);
  const [forecast, setForecast] = useState<ForecastData | null>(null);
  const [loading, setLoading] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const apiKey = process.env.NEXT_PUBLIC_OPENWEATHERMAP_API_KEY;
  const backendUrl = 'https://weather-app-tr3b.onrender.com/predict';

  // Fetch current weather
  const fetchCurrentWeather = async () => {
    setLoading(true);
    try {
      const res = await axios.get(
        `http://api.openweathermap.org/data/2.5/weather?q=${location}&appid=${apiKey}&units=metric`
      );
      setCurrentWeather(res.data);
    } catch (error) {
      console.error('Error fetching current weather:', error);
    }
    setLoading(false);
  };

  // Fetch 7-day forecast for Mandi
  const fetchForecast = async () => {
    try {
      const res = await axios.post(backendUrl, {
        date: new Date().toISOString().split('T')[0],
      });
      setForecast(res.data);
    } catch (error) {
      console.error('Error fetching forecast:', error);
    }
  };

  useEffect(() => {
    fetchCurrentWeather();
    fetchForecast();
  }, []);

  // Handle search
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchCurrentWeather();
    if (window.innerWidth < 768) {
      setSidebarOpen(false);
    }
  };

  // Determine background based on condition
  const getBackgroundImage = () => {
    if (!currentWeather || !currentWeather.weather[0]) return '/background/default.jpg';
    const condition = currentWeather.weather[0].main.toLowerCase();
    if (condition.includes('rain')) return '/background/rainy.jpg';
    if (condition.includes('cloud')) return '/background/cloudy.jpg';
    return '/background/sunny.jpg';
  };

  // Get appropriate weather icon based on condition
  const getWeatherIcon = (condition: string) => {
    switch(condition) {
      case 'sunny':
        return <FiSun size={36} className="text-yellow-400" />;
      case 'cloudy':
        return <FiCloud size={36} className="text-gray-200" />;
      case 'raining':
        return <FiCloudRain size={36} className="text-blue-300" />;
      default:
        return <FiSun size={36} className="text-yellow-400" />;
    }
  };

  return (
    <div 
      className="min-h-screen flex flex-col relative"
      style={{
        backgroundImage: `url(${getBackgroundImage()})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      {/* Mobile menu toggle */}
      <div className="md:hidden absolute top-4 left-4 z-20">
        <button 
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-2 rounded-full bg-black bg-opacity-40 text-white"
        >
          {sidebarOpen ? <FiX size={24} /> : <FiMenu size={24} />}
        </button>
      </div>

      <div className="flex flex-col md:flex-row h-full">
        {/* Left Panel: Current Weather - Smaller width */}
        <div 
          className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'} 
            transform transition-transform duration-300 ease-in-out 
            fixed md:static top-0 left-0 h-full z-10 
            md:w-1/5 p-4 bg-black bg-opacity-25 text-white backdrop-blur-md`}
        >
          <div className="md:hidden flex justify-end">
            <button onClick={() => setSidebarOpen(false)} className="p-1">
              <FiX size={24} />
            </button>
          </div>
          
          <form onSubmit={handleSearch} className="mb-6">
            <div className="flex items-center border-b border-white py-2">
              <FiSearch className="mr-2" />
              <input
                type="text"
                value={location}
                onChange={(e) => setLocation(e.target.value)}
                placeholder="Enter location"
                className="bg-transparent outline-none w-full text-white placeholder-white"
              />
            </div>
          </form>
          {loading && <p>Loading...</p>}
          {currentWeather && (
            <div>
              <h2 className="text-xl font-bold">{currentWeather.name}</h2>
              <div className="flex items-center my-4">
                {currentWeather.weather[0].main.includes('Rain') && <FiCloudRain size={36} />}
                {currentWeather.weather[0].main.includes('Cloud') && <FiCloud size={36} />}
                {currentWeather.weather[0].main.includes('Clear') && <FiSun size={36} />}
                <p className="ml-2 text-4xl">{Math.round(currentWeather.main.temp)}°C</p>
              </div>
              <div className="mt-4 space-y-1 text-sm">
                <div className="flex items-center">
                  <FiDroplet className="mr-2" />
                  <p>Humidity: {Math.round(currentWeather.main.humidity)}%</p>
                </div>
                <div className="flex items-center">
                  <FiWind className="mr-2" />
                  <p>Wind: {currentWeather.wind.speed.toFixed(1)} m/s</p>
                </div>
                <p className="capitalize mt-2">
                  {currentWeather.weather[0].description}
                </p>
              </div>
            </div>
          )}
        </div>

        {/* Right Panel: 7-Day Forecast - Better card layout */}
        <div className="md:w-4/5 p-4 pt-16 md:pt-4">
          <h2 className="text-xl md:text-2xl mb-4 font-bold text-white drop-shadow-lg text-center">
            7-Day Forecast for Mandi
          </h2>
          
          {/* Responsive grid for forecast cards */}
          <div className="max-w-6xl mx-auto">
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-3">
              {forecast &&
                Object.entries(forecast).map(([date, data]: [string, any]) => (
                  <div 
                    key={date} 
                    className="bg-black bg-opacity-20 backdrop-blur-sm p-4 rounded-lg flex flex-col h-48 text-white transition-transform hover:scale-105"
                  >
                    <p className="font-bold text-center text-lg border-b border-gray-400 border-opacity-30 pb-2">
                      {new Date(date).toLocaleDateString('en-GB', { 
                        weekday: 'short', 
                        day: 'numeric', 
                        month: 'short' 
                      })}
                    </p>
                    <div className="flex-grow flex items-center justify-center my-3">
                      {getWeatherIcon(data.condition)}
                    </div>
                    <p className="text-2xl font-bold text-center mb-2">
                      {Math.round(data.temperature)}°C
                    </p>
                    {/* Row layout for precipitation and humidity */}
                    <div className="flex justify-between items-center mt-auto text-xs pt-2 border-t border-gray-400 border-opacity-30">
                      <div className="flex items-center">
                        <FiCloudRain className="mr-1" />
                        <div>{data.precipitation.toFixed(1)}mm</div>
                      </div>
                      <div className="flex items-center">
                        <FiDroplet className="mr-1" />
                        <div>{Math.round(data.humidity)}%</div>
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}