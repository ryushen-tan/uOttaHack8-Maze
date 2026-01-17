import { useEffect, useRef } from 'react';
import { useMap } from 'react-leaflet';
import L from 'leaflet';

function GraphOverlay({ graphData, mapBounds }) {
  const map = useMap();
  const canvasRef = useRef(null);

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

      // Helper to convert lat/lon to pixel coordinates using Leaflet
      const latLonToPixel = (lat, lon) => {
        const point = map.latLngToContainerPoint([lat, lon]);
        return { x: point.x, y: point.y };
      };

      // Draw edges first (so nodes appear on top)
      ctx.strokeStyle = '#00ffff';
      ctx.lineWidth = 2;
      ctx.shadowColor = '#00ffff';
      ctx.shadowBlur = 2;
      
      graphData.edges.forEach(edge => {
        const start = latLonToPixel(edge.start.y, edge.start.x); // Note: lat is y, lon is x
        const end = latLonToPixel(edge.end.y, edge.end.x);
        
        ctx.beginPath();
        ctx.moveTo(start.x, start.y);
        ctx.lineTo(end.x, end.y);
        ctx.stroke();
      });
      ctx.shadowBlur = 0;

      // Draw nodes
      graphData.nodes.forEach(node => {
        const pos = latLonToPixel(node.y, node.x); // Note: lat is y, lon is x
        // Draw outline for better visibility
        ctx.fillStyle = '#ffffff';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 2, 0, Math.PI * 2);
        ctx.fill();
        // Draw inner node
        ctx.fillStyle = '#00ffff';
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 1.5, 0, Math.PI * 2);
        ctx.fill();
      });
    };

    // Initial draw
    redraw();

    // Redraw when map moves or zooms
    map.on('moveend', redraw);
    map.on('zoomend', redraw);
    map.on('resize', redraw);

    return () => {
      map.off('moveend', redraw);
      map.off('zoomend', redraw);
      map.off('resize', redraw);
    };
  }, [graphData, mapBounds, map]);

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 pointer-events-none z-[1000]"
      style={{ pointerEvents: 'none' }}
    />
  );
}

export default GraphOverlay;
