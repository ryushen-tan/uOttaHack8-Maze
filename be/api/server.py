from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os
import osmnx as ox
from osmnx import utils_geo, projection

ox.settings.max_query_area_size = 50 * 1000 * 1000  # 50 km² in square meters

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataFetch import Location
from World import World

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
apiPrefix = '/api'

@app.route(f'{apiPrefix}/graph', methods=['POST'])
def get_graph():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        bounds = data.get('bounds')  # Expects [min_lat, max_lat, min_lon, max_lon]
        
        if not bounds or len(bounds) != 4:
            return jsonify({'error': f'Invalid bounds. Expected [min_lat, max_lat, min_lon, max_lon], got: {bounds}'}), 400
            
        min_lat, max_lat, min_lon, max_lon = bounds
        
        # Convert to OSMNX bbox format: (left, bottom, right, top)
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        # Use OSMNX's own area calculation method (projected to Web Mercator)
        # This matches how OSMNX internally calculates area for validation
        polygon = utils_geo.bbox_to_poly(bbox)
        polygon_proj, crs = projection.project_geometry(polygon)
        projected_area_m2 = polygon_proj.area
        projected_area_km2 = projected_area_m2 / 1000000
        
        # Also calculate geographic area for user feedback
        import math
        avg_lat = (min_lat + max_lat) / 2
        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon
        lat_meters = lat_diff * 111000
        lon_meters = lon_diff * 111000 * math.cos(math.radians(avg_lat))
        geographic_area_km2 = (lat_meters * lon_meters) / 1000000
        
        # Limit to reasonable size using OSMNX's projected area calculation
        MAX_AREA_KM2 = 50
        if projected_area_km2 > MAX_AREA_KM2:
            return jsonify({
                'error': f'Area too large ({geographic_area_km2:.2f} km² geographic, {projected_area_km2:.2f} km² projected). Maximum allowed: {MAX_AREA_KM2} km². Please zoom in more on the map.',
                'area_km2': geographic_area_km2,
                'projected_area_km2': projected_area_km2,
                'max_allowed': MAX_AREA_KM2
            }), 400
        
        print(f"Received bounds: {bounds} (Geographic area: {geographic_area_km2:.2f} km², Projected area: {projected_area_km2:.2f} km², {projected_area_m2:.0f} m²)")
        
        # Create location from bounds
        location = Location(bounds=bounds)
        world = World(location)

        print("Location created successfully")
        
        # Get graph
        graph = world.graph
        print(f"Graph created with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        
        # Return as JSON
        result = graph.to_dict()
        print("Graph converted to dict successfully")
        return jsonify(result)
        
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in get_graph: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({'error': str(e), 'traceback': error_trace}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)