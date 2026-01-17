import { useState, useEffect, useRef } from 'react';
import Map from '../components/Map';

const Snow = () => {
    const [mapCenter, setMapCenter] = useState(null);
    const [input, setInput] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [locationSelected, setLocationSelected] = useState(false);
    const suggestionsRef = useRef(null);
    const debounceTimer = useRef(null);

    // Geocode using OpenStreetMap Nominatim (free, no API key needed)
    const handleGeocode = async (query) => {
        if (!query.trim()) {
            setSuggestions([]);
            return;
        }

        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5`,
                {
                    headers: {
                        'User-Agent': 'MazeApp/1.0' // Required by Nominatim
                    }
                }
            );
            const data = await response.json();
            setSuggestions(data);
        } catch (error) {
            console.error('Geocoding error:', error);
            setSuggestions([]);
        }
    };

    const handleInput = (e) => {
        const value = e.target.value;
        setInput(value);
        setShowSuggestions(true);

        // Debounce the geocoding request
        if (debounceTimer.current) {
            clearTimeout(debounceTimer.current);
        }

        debounceTimer.current = setTimeout(() => {
            handleGeocode(value);
        }, 300);
    };

    const handleSelect = (suggestion) => {
        setInput(suggestion.display_name);
        setMapCenter([parseFloat(suggestion.lat), parseFloat(suggestion.lon)]);
        setLocationSelected(true);
        setShowSuggestions(false);
        setSuggestions([]);
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (suggestionsRef.current && !suggestionsRef.current.contains(event.target)) {
                setShowSuggestions(false);
            }
        };

        document.addEventListener('mousedown', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            if (debounceTimer.current) {
                clearTimeout(debounceTimer.current);
            }
        };
    }, []);

    return (
        <div className="h-screen w-screen bg-gradient-to-b from-black via-[#0a0a0a] to-[#1a1a1a] flex flex-col p-[10px]">
            <div className="w-full h-[120px] rounded-t-3xl backdrop-blur-md bg-white/10 border-2 border-white/20 shadow-lg p-6 flex items-center relative z-[10002]" ref={suggestionsRef}>
                <input
                    type="text"
                    value={input}
                    onChange={handleInput}
                    onFocus={() => setShowSuggestions(true)}
                    placeholder="Enter a location (e.g., Ottawa, Ontario)..."
                    className="w-full px-4 py-3 rounded-xl bg-black/30 border-2 border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400/50 focus:border-pink-400/50 transition-all"
                    style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                />
                {showSuggestions && suggestions.length > 0 && (
                    <ul className="absolute top-full left-6 right-6 mt-2 bg-black/90 backdrop-blur-md border-2 border-white/20 rounded-xl shadow-lg z-[10001] max-h-60 overflow-y-auto">
                        {suggestions.map((suggestion, index) => (
                            <li
                                key={suggestion.place_id || index}
                                onClick={() => handleSelect(suggestion)}
                                className="px-4 py-3 text-white hover:bg-white/10 cursor-pointer transition-colors border-b border-white/10 last:border-b-0"
                                style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                            >
                                {suggestion.display_name}
                            </li>
                        ))}
                    </ul>
                )}
            </div>

            <div className="w-full flex-1 rounded-b-3xl backdrop-blur-md bg-white/10 border border-white/20 border-t-0 shadow-lg p-6">
                {!locationSelected ? (
                    <div className='w-full h-full bg-gray-800 p-5 rounded-2xl fade-loading'>
                    </div>
                ) : (
                    <div className='w-full h-full rounded-2xl overflow-hidden'>
                        <Map center={mapCenter} />
                    </div>
                )}
            </div>
        </div>
    );
};

export default Snow;