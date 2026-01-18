from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import sys
import os
import osmnx as ox
from osmnx import utils_geo, projection
import threading
import time
import math
import traceback
import hashlib
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from DataFetch import Location
from World import World

ox.settings.use_cache = True
ox.settings.log_console = False
ox.settings.max_query_area_size = 25 * 1000 * 1000

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
apiPrefix = '/api'

cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api', 'cache')
os.makedirs(cache_dir, exist_ok=True)

def get_cache_key(bounds):
    bounds_str = json.dumps(bounds, sort_keys=True)
    return hashlib.md5(bounds_str.encode()).hexdigest()

def get_cached_graph(bounds):
    cache_key = get_cache_key(bounds)
    cache_file = os.path.join(cache_dir, f'{cache_key}.json')
    
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Cache read error: {e}")
            pass
    return None

def cache_graph(bounds, graph_dict):
    cache_key = get_cache_key(bounds)
    cache_file = os.path.join(cache_dir, f'{cache_key}.json')
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(graph_dict, f)
    except (IOError, OSError) as e:
        print(f"Cache write error: {e}")
        pass

@app.route(f'{apiPrefix}/graph', methods=['POST'])
def get_graph():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No JSON data received'}), 400
            
        bounds = data.get('bounds')
        
        if not bounds or len(bounds) != 4:
            return jsonify({'error': f'Invalid bounds. Expected [min_lat, max_lat, min_lon, max_lon], got: {bounds}'}), 400
            
        min_lat, max_lat, min_lon, max_lon = bounds
        
        bbox = (min_lon, min_lat, max_lon, max_lat)
        
        polygon = utils_geo.bbox_to_poly(bbox)
        polygon_proj, crs = projection.project_geometry(polygon)
        projected_area_m2 = polygon_proj.area
        projected_area_km2 = projected_area_m2 / 1000000
        
        avg_lat = (min_lat + max_lat) / 2
        lat_diff = max_lat - min_lat
        lon_diff = max_lon - min_lon
        lat_meters = lat_diff * 111000
        lon_meters = lon_diff * 111000 * math.cos(math.radians(avg_lat))
        geographic_area_km2 = (lat_meters * lon_meters) / 1000000
        
        MAX_AREA_KM2 = 25
        if projected_area_km2 > MAX_AREA_KM2:
            return jsonify({
                'error': f'Area too large ({geographic_area_km2:.2f} km² geographic, {projected_area_km2:.2f} km² projected). Maximum allowed: {MAX_AREA_KM2} km². Please zoom in more on the map.',
                'area_km2': geographic_area_km2,
                'projected_area_km2': projected_area_km2,
                'max_allowed': MAX_AREA_KM2
            }), 400
        
        cached_result = get_cached_graph(bounds)
        if cached_result:
            print(f"Returning cached graph for bounds: {bounds}")
            return jsonify(cached_result)
        
        print(f"Fetching graph for bounds: {bounds} (Geographic area: {geographic_area_km2:.2f} km², Projected area: {projected_area_km2:.2f} km²)")
        start_time = time.time()
        
        location = Location(bounds=bounds)
        world = World(location, 0)

        graph = world.graph
        print(f"Graph created with {len(graph.nodes)} nodes and {len(graph.edges)} edges in {time.time() - start_time:.2f} seconds")
        
        result = graph.to_dict()
        cache_graph(bounds, result)
        print("Graph cached successfully")
        
        return jsonify(result)
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in get_graph: {str(e)}")
        print(f"Traceback: {error_trace}")
        return jsonify({'error': str(e), 'traceback': error_trace}), 500

@socketio.on('start_simulation')
def handle_start_simulation(data):
    
    try:
        bounds = data.get('bounds')
        num_workers = data.get('num_workers', 10)
        session_id = data.get('session_id', f'session_{time.time()}')
        client_sid = request.sid
        
        if not bounds or len(bounds) != 4:
            emit('error', {'message': 'Invalid bounds. Expected [min_lat, max_lat, min_lon, max_lon]'})
            return
        
        print(f"Starting simulation for session {session_id} with {num_workers} workers")
        
        location = Location(bounds=bounds)
        world = World(location, num_workers)
        
        graph = world.graph
        graph_dict = graph.to_dict()
        workers_list = graph.get_workers_dict(world.workers)
        progress = graph.clean_ratio()
        
        initial_state = {
            **graph_dict,
            'workers': workers_list,
            'progress': progress
        }
        emit('initial_state', initial_state)
        
        def run_simulation():
            update_interval = 0.8
            last_update = time.time()
            
            while not world.is_finished():
                world.play()
                
                current_time = time.time()
                if current_time - last_update >= update_interval:
                    graph_dict = graph.to_dict()
                    workers_list = graph.get_workers_dict(world.workers)
                    progress = graph.clean_ratio()
                    
                    update_data = {
                        'workers': workers_list,
                        'edges': graph_dict['edges'],
                        'progress': progress
                    }
                    
                    socketio.emit('update', update_data, room=client_sid)
                    last_update = current_time
                
                time.sleep(0.1)
            
            graph_dict = graph.to_dict()
            workers_list = graph.get_workers_dict(world.workers)
            final_state = {
                'workers': workers_list,
                'edges': graph_dict['edges'],
                'progress': 1.0
            }
            socketio.emit('final_state', final_state, room=client_sid)
            print(f"Simulation completed for session {session_id}")
        
        thread = threading.Thread(target=run_simulation, daemon=True)
        thread.start()
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in start_simulation: {str(e)}")
        print(f"Traceback: {error_trace}")
        emit('error', {'message': str(e), 'traceback': error_trace})

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)