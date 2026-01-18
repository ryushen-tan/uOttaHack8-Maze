import { useState, useEffect, useRef } from 'react';
import Map from '../components/Map';
import GraphOverlay from '../components/GraphOverlay';

const Snow = () => {
    const [mapCenter, setMapCenter] = useState(null);
    const [input, setInput] = useState('');
    const [suggestions, setSuggestions] = useState([]);
    const [showSuggestions, setShowSuggestions] = useState(false);
    const [selectedSuggestion, setSelectedSuggestion] = useState(null);
    const [locationSelected, setLocationSelected] = useState(false);
    const [graphData, setGraphData] = useState(null);
    const [mapBounds, setMapBounds] = useState(null);
    const [loadingGraph, setLoadingGraph] = useState(false);
    const [showGraph, setShowGraph] = useState(false);
    const [numWorkers, setNumWorkers] = useState(10);
    const [simulationStarted, setSimulationStarted] = useState(false);
    const suggestionsRef = useRef(null);
    const debounceTimer = useRef(null);

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
        setSelectedSuggestion(null);
        setShowSuggestions(true);

        if (debounceTimer.current) {
            clearTimeout(debounceTimer.current);
        }

        debounceTimer.current = setTimeout(() => {
            handleGeocode(value);
        }, 300);
    };

    const handleSelectSuggestion = (suggestion) => {
        setInput(suggestion.display_name);
        setSelectedSuggestion(suggestion);
        setShowSuggestions(false);
    };

    const handleGo = () => {
        if (!selectedSuggestion && suggestions.length > 0) {
            setSelectedSuggestion(suggestions[0]);
        }
        
        if (selectedSuggestion || suggestions.length > 0) {
            const suggestion = selectedSuggestion || suggestions[0];
            setMapCenter([parseFloat(suggestion.lat), parseFloat(suggestion.lon)]);
            setLocationSelected(true);
            setShowSuggestions(false);
            setSuggestions([]);
            setGraphData(null);
            setShowGraph(false);
            setSimulationStarted(false);
        }
    };

    const handleBoundsChange = async (bounds) => {
        if (!bounds || !bounds.osmnxFormat) return;
        
        setLoadingGraph(true);
        setShowGraph(false);
        setMapBounds(bounds); // Store the map bounds used to fetch the graph
        
        try {
            // Add timeout (30 seconds)
            const controller = new AbortController();            
            const response = await fetch('http://127.0.0.1:5000/api/graph', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ bounds: bounds.osmnxFormat }),
                signal: controller.signal
            });
                        
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.error || `HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            setGraphData(data);
            setShowGraph(true);
            setSimulationStarted(false);
        } catch (error) {
            console.error('Error fetching graph:', error);
            if (error.name === 'AbortError') {
                alert('Request timed out. The area might be too large. Try zooming in more on the map before getting bounds.');
            } else {
                alert(error.message || 'Failed to fetch graph. Make sure the backend server is running on http://127.0.0.1:5000');
            }
        } finally {
            setLoadingGraph(false);
        }
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
            <div className="w-full flex-1 rounded-2xl backdrop-blur-md bg-white/10 border border-white/20 shadow-lg p-6 relative">
                {!locationSelected ? (
                    <div className='w-full h-full bg-gray-800 p-5 rounded-2xl fade-loading'>
                    </div>
                ) : (
                    <div className='w-full h-full rounded-2xl overflow-hidden relative'>
                        <Map 
                            center={mapCenter} 
                            resetKey={mapCenter?.join(',')} 
                            onBoundsChange={handleBoundsChange}
                            hideControls={showGraph}
                        >
                            {showGraph && graphData && mapBounds && (
                                <GraphOverlay 
                                    graphData={graphData} 
                                    mapBounds={mapBounds} 
                                    numWorkers={simulationStarted ? numWorkers : null} 
                                />
                            )}
                        </Map>
                        {loadingGraph && (
                            <div className="absolute inset-0 bg-black/50 flex items-center justify-center z-[2000]">
                                <div className="text-white text-xl" style={{ fontFamily: 'Rubik Pixels, sans-serif' }}>
                                    Loading graph...
                                </div>
                            </div>
                        )}
                        
                        {graphData && (
                            <button
                                onClick={() => setShowGraph(!showGraph)}
                                className="hover:cursor-pointer absolute top-6 left-6 px-4 py-2 bg-white/10 backdrop-blur-md border-2 border-white/20 text-white rounded-xl hover:bg-white/20 transition-all shadow-lg z-[4000]"
                                style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                            >
                                {showGraph ? 'Hide Graph' : 'Show Graph'}
                            </button>
                        )}
                        
                        
                    </div>
                )}
            </div>

            {!locationSelected && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[20000] p-4">
                    <div 
                        className="backdrop-blur-md bg-white/10 border-2 border-white/20 rounded-3xl shadow-2xl p-8 w-full max-w-2xl relative"
                        ref={suggestionsRef}
                    >
                        <h2 className="text-white text-2xl mb-6 text-center" style={{ fontFamily: 'Rubik Pixels, sans-serif' }}>
                            Enter Location
                        </h2>
                        <div className="flex gap-3 mb-4">
                            <input
                                type="text"
                                value={input}
                                onChange={handleInput}
                                onFocus={() => setShowSuggestions(true)}
                                placeholder="Enter a location (e.g., Ottawa, Ontario)..."
                                className="flex-1 px-4 py-3 rounded-xl bg-black/30 border-2 border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400/50 focus:border-pink-400/50 transition-all"
                                style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                                autoFocus
                            />
                            <input
                                type="number"
                                value={numWorkers}
                                onChange={(e) => setNumWorkers(Math.max(1, parseInt(e.target.value) || 1))}
                                min="1"
                                placeholder="Workers"
                                className="w-24 px-4 py-3 rounded-xl bg-black/30 border-2 border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400/50 focus:border-pink-400/50 transition-all"
                                style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                            />
                            <button
                                onClick={handleGo}
                                disabled={!input.trim() || numWorkers < 1 || suggestions.length === 0}
                                className="px-6 py-3 rounded-xl bg-pink-500/80 hover:bg-pink-500 disabled:bg-gray-500/50 disabled:cursor-not-allowed text-white font-bold transition-all border-2 border-pink-400/50"
                                style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                            >
                                Go
                            </button>
                        </div>
                        {showSuggestions && suggestions.length > 0 && (
                            <ul className="mt-4 bg-black/90 backdrop-blur-md border-2 border-white/20 rounded-xl shadow-lg max-h-60 overflow-y-auto">
                                {suggestions.map((suggestion, index) => (
                                    <li
                                        key={suggestion.place_id || index}
                                        onClick={() => handleSelectSuggestion(suggestion)}
                                        className={`px-4 py-3 text-white hover:bg-white/10 cursor-pointer transition-colors border-b border-white/10 last:border-b-0 ${
                                            selectedSuggestion?.place_id === suggestion.place_id ? 'bg-pink-500/30' : ''
                                        }`}
                                        style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                                    >
                                        {suggestion.display_name}
                                    </li>
                                ))}
                            </ul>
                        )}
                    </div>
                </div>
            )}
            
            {locationSelected && graphData && (
                <div className="fixed bottom-6 left-1/2 -translate-x-1/2 z-[20000]">
                    <div className="backdrop-blur-md bg-white/10 border-2 border-white/20 rounded-xl shadow-2xl p-4 flex gap-3 items-center">
                        <input
                            type="number"
                            value={numWorkers}
                            onChange={(e) => {
                                const newValue = Math.max(1, parseInt(e.target.value) || 1);
                                setNumWorkers(newValue);
                                if (simulationStarted) {
                                    setSimulationStarted(false);
                                }
                            }}
                            min="1"
                            placeholder="Workers"
                            className="w-24 px-4 py-3 rounded-xl bg-black/30 border-2 border-white/20 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-pink-400/50 focus:border-pink-400/50 transition-all"
                            style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                        />
                        <button
                            onClick={() => setSimulationStarted(!simulationStarted)}
                            className={`px-6 py-3 rounded-xl font-bold transition-all border-2 ${
                                simulationStarted 
                                    ? 'bg-red-500/80 hover:bg-red-500 border-red-400/50' 
                                    : 'bg-pink-500/80 hover:bg-pink-500 border-pink-400/50'
                            } text-white`}
                            style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
                        >
                            {simulationStarted ? 'Stop Simulation' : 'Start Simulation'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Snow;