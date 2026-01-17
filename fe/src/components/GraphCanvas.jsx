import { useEffect, useRef } from 'react';

function GraphCanvas({ graphData, width = 1300, height = 500 }) {
  const canvasRef = useRef(null);

  useEffect(() => {
    if (!graphData || !canvasRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const canvasWidth = canvas.width;
    const canvasHeight = canvas.height;

    // Clear canvas with transparent background
    ctx.clearRect(0, 0, canvasWidth, canvasHeight);

    // Helper to convert graph coordinates to screen coordinates
    const graphToScreen = (node) => {
      const { bounds } = graphData;
      const graphWidth = bounds.right - bounds.left;
      const graphHeight = bounds.up - bounds.down;
      
      if (graphWidth === 0 || graphHeight === 0) {
        return { x: 0, y: 0 };
      }
      
      const x = ((node.x - bounds.left) / graphWidth) * canvasWidth;
      const y = canvasHeight - ((node.y - bounds.down) / graphHeight) * canvasHeight; // Flip Y axis
      return { x, y };
    };

    // Draw edges first (so nodes appear on top)
    // Use bright cyan/blue with slight glow for visibility on map
    ctx.strokeStyle = '#00ffff';
    ctx.lineWidth = 2;
    ctx.shadowColor = '#00ffff';
    ctx.shadowBlur = 2;
    graphData.edges.forEach(edge => {
      const start = graphToScreen(edge.start);
      const end = graphToScreen(edge.end);
      
      ctx.beginPath();
      ctx.moveTo(start.x, start.y);
      ctx.lineTo(end.x, end.y);
      ctx.stroke();
    });
    ctx.shadowBlur = 0; // Reset shadow

    // Draw nodes with bright color and outline for visibility
    graphData.nodes.forEach(node => {
      const pos = graphToScreen(node);
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
  }, [graphData, width, height]);

  return (
    <canvas
      ref={canvasRef}
      width={width}
      height={height}
      className="w-full h-full"
      style={{ background: 'transparent' }}
    />
  );
}

export default GraphCanvas;
