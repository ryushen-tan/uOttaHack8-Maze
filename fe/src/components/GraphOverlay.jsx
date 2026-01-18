import { useEffect, useRef, useState } from 'react';
import { useMap } from 'react-leaflet';
import { io } from 'socket.io-client';
import { toast } from 'react-toastify';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// Road priority enum values (matching backend)
const RoadPriority = {
  MOTORWAY_LINK: 0,
  MOTORWAY: 0,
  TRUNK: 1,
  PRIMARY: 2,
  SECONDARY: 3,
  TERTIARY: 4,
  RESIDENTIAL: 5,
  UNCLASSIFIED: 6
};

// Priority color mapping (matching Game.py)
const getPriorityColor = (priority) => {
  switch (priority) {
    case RoadPriority.MOTORWAY_LINK:
    case RoadPriority.MOTORWAY:
      return '#8B0000'; // Dark red
    case RoadPriority.TRUNK:
      return '#FF0000'; // Red
    case RoadPriority.PRIMARY:
      return '#FF8C00'; // Dark orange
    case RoadPriority.SECONDARY:
      return '#FFD700'; // Gold
    case RoadPriority.TERTIARY:
      return '#87CEEB'; // Sky blue
    case RoadPriority.RESIDENTIAL:
    case RoadPriority.UNCLASSIFIED:
      return '#D3D3D3'; // Light gray
    default:
      return '#D3D3D3'; // Light gray
  }
};

const getPriorityName = (priority) => {
  switch (priority) {
    case RoadPriority.MOTORWAY_LINK:
    case RoadPriority.MOTORWAY:
      return 'Motorway';
    case RoadPriority.TRUNK:
      return 'Trunk';
    case RoadPriority.PRIMARY:
      return 'Primary';
    case RoadPriority.SECONDARY:
      return 'Secondary';
    case RoadPriority.TERTIARY:
      return 'Tertiary';
    case RoadPriority.RESIDENTIAL:
      return 'Residential';
    case RoadPriority.UNCLASSIFIED:
      return 'Unclassified';
    default:
      return 'Unknown';
  }
};

function GraphOverlay({ graphData, mapBounds, numWorkers, onProgressUpdate }) {
  const map = useMap();
  const canvasRef = useRef(null);
  const [liveData, setLiveData] = useState(null);
  const [progress, setProgress] = useState(0);
  const socketRef = useRef(null);
  const imageRef = useRef(null);
  const [showLegend, setShowLegend] = useState(true);

  const mergeLiveData = (prev, data) => {
    if (!prev) {
      return {
        ...graphData,
        workers: data.workers || [],
        edges: data.edges || graphData.edges,
        progress: data.progress !== undefined ? data.progress : 0
      };
    }
    return {
      ...prev,
      workers: data.workers !== undefined ? data.workers : prev.workers,
      edges: data.edges !== undefined ? data.edges : prev.edges,
      progress: data.progress !== undefined ? data.progress : prev.progress
    };
  };

  useEffect(() => {
    const img = new Image();
    img.src = '/snow_plow.png';
    img.onload = () => {
      imageRef.current = img;
    };
    img.onerror = () => {
      console.warn('Failed to load snow plow image');
    };
  }, []);

  useEffect(() => {
    if (!graphData || !mapBounds) return;

    if (!numWorkers) {
      setLiveData(null);
      setProgress(0);
      return;
    }

    const socket = io(API_URL);
    socketRef.current = socket;

    const sessionId = `session_${Date.now()}`;

    socket.on('connect', () => {
      console.log('WebSocket connected');
      socket.emit('start_simulation', {
        bounds: mapBounds.osmnxFormat,
        num_workers: numWorkers,
        session_id: sessionId
      });
    });

    socket.on('initial_state', (data) => {
      console.log('Received initial_state:', data);
      setLiveData(data);
      setProgress(data.progress || 0);
      if (onProgressUpdate) onProgressUpdate(data.progress || 0);
    });

    socket.on('update', (data) => {
      console.log('Received update:', data);
      setLiveData(prev => mergeLiveData(prev, data));
      setProgress(data.progress || 0);
      if (onProgressUpdate) onProgressUpdate(data.progress || 0);
    });

    socket.on('final_state', (data) => {
      setLiveData(prev => mergeLiveData(prev, { ...data, progress: 1.0 }));
      setProgress(1.0);
      if (onProgressUpdate) onProgressUpdate(1.0);
    });

    socket.on('error', (data) => {
      console.error('WebSocket error:', data);
      toast.error(data.message || 'WebSocket connection error');
    });

    return () => {
      socket.disconnect();
      socketRef.current = null;
    };
  }, [graphData, mapBounds, numWorkers, onProgressUpdate]);

  useEffect(() => {
    if (!graphData || !mapBounds || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const mapContainer = map.getContainer();
    const dpr = window.devicePixelRatio || 1;

    const redraw = () => {
      // Get current container size
      const containerRect = mapContainer.getBoundingClientRect();
      const width = containerRect.width;
      const height = containerRect.height;
      
      // Update canvas size to match container
      canvas.width = width * dpr;
      canvas.height = height * dpr;
      canvas.style.width = `${width}px`;
      canvas.style.height = `${height}px`;
      
      // Reset transform and scale
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.scale(dpr, dpr);
      
      // Clear canvas
      ctx.clearRect(0, 0, width, height);

      // Use live data if available, otherwise use initial graph data
      const dataToRender = liveData || graphData;

      const latLonToPixel = (lat, lon) => {
        const point = map.latLngToContainerPoint([lat, lon]);
        return { x: point.x, y: point.y };
      };

      // Draw edges with transparency
      ctx.globalAlpha = 0.7; // 70% opacity for slight transparency
      
      dataToRender.edges.forEach(edge => {
        const start = latLonToPixel(edge.start.y, edge.start.x);
        const end = latLonToPixel(edge.end.y, edge.end.x);
        
        // Use green for cleaned roads, otherwise use priority color
        if (edge.clean) {
          ctx.strokeStyle = '#00ff00';
        } else {
          const priority = edge.priority !== undefined ? edge.priority : RoadPriority.UNCLASSIFIED;
          const color = getPriorityColor(priority);
          ctx.strokeStyle = color;
        }
        
        // Thinner lines - reduced from 1.5/2.5 to 0.8/1.2
        ctx.lineWidth = edge.oneway ? 0.8 : 1.2;
        ctx.beginPath();
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(end.x, end.y);
        ctx.stroke();
      });
      
      // Reset alpha for workers
      ctx.globalAlpha = 1.0;

      // Nodes are not rendered - only edges and workers are shown
      if (dataToRender.workers && dataToRender.workers.length > 0 && imageRef.current) {
        const img = imageRef.current;
        const imgSize = 20;
        dataToRender.workers.forEach(worker => {
          const pos = latLonToPixel(worker.y, worker.x);
          ctx.drawImage(img, pos.x - imgSize / 2, pos.y - imgSize / 2, imgSize, imgSize);
        });
      }
    };

    redraw();

    map.on('moveend', redraw);
    map.on('zoomend', redraw);
    map.on('resize', redraw);

    return () => {
      map.off('moveend', redraw);
      map.off('zoomend', redraw);
      map.off('resize', redraw);
    };
  }, [graphData, mapBounds, map, liveData]);

  // Get unique priorities for legend
  const getUniquePriorities = () => {
    const dataToRender = liveData || graphData;
    if (!dataToRender || !dataToRender.edges) return [];
    
    const priorities = new Set();
    dataToRender.edges.forEach(edge => {
      if (edge.priority !== undefined) {
        priorities.add(edge.priority);
      }
    });
    
    // Return sorted priorities (0-6)
    return Array.from(priorities).sort((a, b) => a - b);
  };

  const uniquePriorities = getUniquePriorities();

  return (
    <>
      <canvas
        ref={canvasRef}
        className="absolute inset-0 pointer-events-none z-[1000]"
        style={{ pointerEvents: 'none' }}
      />
      {progress > 0 && (
        <div className="absolute top-4 right-4 bg-black/80 backdrop-blur-md border-2 border-white/20 text-white rounded-xl p-4 z-[2000] min-w-[200px]">
          <div className="text-sm mb-2" style={{ fontFamily: 'Rubik Pixels, sans-serif' }}>
            Progress: {(progress * 100).toFixed(1)}%
          </div>
          <div className="w-full h-2 bg-white/20 rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-green-500 to-green-400 rounded-full transition-all duration-300"
              style={{ width: `${progress * 100}%` }}
            />
          </div>
        </div>
      )}
      {showLegend && uniquePriorities.length > 0 && (
        <div className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-md border-2 border-white/20 text-white rounded-xl p-4 z-[2000] max-w-[250px]">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm font-bold" style={{ fontFamily: 'Rubik Pixels, sans-serif' }}>
              Road Priority
            </div>
            <button
              onClick={() => setShowLegend(false)}
              className="text-white/60 hover:text-white transition-colors text-lg"
              style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
            >
              ×
            </button>
          </div>
          <div className="space-y-2">
            {uniquePriorities.map(priority => (
              <div key={priority} className="flex items-center gap-2">
                <div
                  className="w-6 h-1.5 rounded"
                  style={{ backgroundColor: getPriorityColor(priority) }}
                />
                <span className="text-xs" style={{ fontFamily: 'Rubik Pixels, sans-serif' }}>
                  {getPriorityName(priority)}
                </span>
              </div>
            ))}
            <div className="flex items-center gap-2 mt-3 pt-3 border-t border-white/20">
              <div className="w-6 h-1.5 rounded bg-green-500" />
              <span className="text-xs" style={{ fontFamily: 'Rubik Pixels, sans-serif' }}>
                Cleaned
              </span>
            </div>
          </div>
        </div>
      )}
      {!showLegend && (
        <button
          onClick={() => setShowLegend(true)}
          className="absolute bottom-4 left-4 bg-black/80 backdrop-blur-md border-2 border-white/20 text-white rounded-xl px-3 py-2 z-[2000] hover:bg-black/90 transition-colors"
          style={{ fontFamily: 'Rubik Pixels, sans-serif' }}
        >
          Show Legend
        </button>
      )}
    </>
  );
}

export default GraphOverlay;
