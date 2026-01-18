import { useEffect, useRef, useState } from 'react';
import { useMap } from 'react-leaflet';
import { io } from 'socket.io-client';

function GraphOverlay({ graphData, mapBounds, numWorkers, onProgressUpdate }) {
  const map = useMap();
  const canvasRef = useRef(null);
  const [liveData, setLiveData] = useState(null);
  const [progress, setProgress] = useState(0);
  const socketRef = useRef(null);
  const imageRef = useRef(null);

  useEffect(() => {
    const img = new Image();
    img.src = '/snow_plow.png';
    img.onload = () => {
      imageRef.current = img;
    };
  }, []);

  useEffect(() => {
    if (!graphData || !mapBounds) return;

    if (!numWorkers) {
      setLiveData(null);
      setProgress(0);
      return;
    }

    const socket = io('http://127.0.0.1:5000');
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
      setLiveData(prev => {
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
      });
      setProgress(data.progress || 0);
      if (onProgressUpdate) onProgressUpdate(data.progress || 0);
    });

    socket.on('final_state', (data) => {
      setLiveData(prev => {
        if (!prev) {
          return {
            ...graphData,
            workers: data.workers || [],
            edges: data.edges || graphData.edges,
            progress: 1.0
          };
        }
        return {
          ...prev,
          workers: data.workers !== undefined ? data.workers : prev.workers,
          edges: data.edges !== undefined ? data.edges : prev.edges,
          progress: 1.0
        };
      });
      setProgress(1.0);
      if (onProgressUpdate) onProgressUpdate(1.0);
    });

    socket.on('error', (data) => {
      console.error('WebSocket error:', data);
    });

    return () => {
      socket.disconnect();
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

      ctx.shadowBlur = 2;
      
      dataToRender.edges.forEach(edge => {
        const start = latLonToPixel(edge.start.y, edge.start.x);
        const end = latLonToPixel(edge.end.y, edge.end.x);
        
        if (edge.clean) {
          ctx.strokeStyle = '#00ff00';
          ctx.shadowColor = '#00ff00';
        } else {
          ctx.strokeStyle = '#00ffff';
          ctx.shadowColor = '#00ffff';
        }
        
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(end.x, end.y);
        ctx.stroke();
      });
      ctx.shadowBlur = 0;

      dataToRender.nodes.forEach(node => {
        const pos = latLonToPixel(node.y, node.x);
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 2, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#00ffff';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      });

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
    </>
  );
}

export default GraphOverlay;
