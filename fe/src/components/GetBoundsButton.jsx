import { useState, useEffect } from "react";
import { useMap, Rectangle } from "react-leaflet";

function GetBoundsButton({ onBoundsChange, resetKey }) {
  const map = useMap();
  const [bounds, setBounds] = useState(null);
  const [showRectangle, setShowRectangle] = useState(false);

  // Reset bounds when location changes (resetKey changes)
  useEffect(() => {
    setBounds(null);
    setShowRectangle(false);
  }, [resetKey]);

  const handleGetBounds = () => {
    const mapBounds = map.getBounds();
    const cornerCoords = {
      north: mapBounds.getNorth(),
      south: mapBounds.getSouth(),
      east: mapBounds.getEast(),
      west: mapBounds.getWest(),
      osmnxFormat: [
        mapBounds.getSouth(), // min_lat
        mapBounds.getNorth(), // max_lat
        mapBounds.getWest(),  // min_lon
        mapBounds.getEast()   // max_lon
      ]
    };
    setBounds(cornerCoords);
    setShowRectangle(true);
    if (onBoundsChange) {
      onBoundsChange(cornerCoords);
    }
    console.log('Map Bounds:', cornerCoords);
  };

  return (
    <>
      {/* Visual rectangle overlay showing bounds */}
      {showRectangle && bounds && (
        <Rectangle
          bounds={[
            [bounds.south, bounds.west],
            [bounds.north, bounds.east]
          ]}
          pathOptions={{
            color: '#ff6b6b',
            fillColor: '#ff6b6b',
            fillOpacity: 0.1,
            weight: 2
          }}
        />
      )}
      
      <div className="absolute top-4 right-4 z-[1000] flex flex-col gap-2">
        <button
          onClick={handleGetBounds}
          className="px-4 py-2 bg-white/10 backdrop-blur-md border-2 border-white/20 text-white rounded-xl hover:bg-white/20 transition-all shadow-lg"
          style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
        >
          Get Bounds
        </button>
        {bounds && (
          <div className="bg-black/90 backdrop-blur-md border-2 border-white/20 text-white rounded-xl p-4 text-xs max-w-xs shadow-lg">
            <div className="mb-2 font-semibold">Corner Coordinates:</div>
            <div>North: {bounds.north.toFixed(6)}</div>
            <div>South: {bounds.south.toFixed(6)}</div>
            <div>East: {bounds.east.toFixed(6)}</div>
            <div>West: {bounds.west.toFixed(6)}</div>
            <div className="mt-2 pt-2 border-t border-white/20">
              <div className="font-semibold mb-1">OSMNX Format:</div>
              <div className="font-mono text-[10px]">
                [{bounds.osmnxFormat.map(coord => coord.toFixed(6)).join(', ')}]
              </div>
            </div>
          </div>
        )}
      </div>
    </>
  );
}

export default GetBoundsButton;
