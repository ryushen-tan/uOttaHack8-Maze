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

from Location import Location
from World import World

from constants import SIMULATION_UPDATE_INTERVAL, SIMULATION_STEP_DELAY
from training_session import TrainingSession

ox.settings.use_cache = True
ox.settings.log_console = False
# ox.settings.max_query_area_size = 25 * 1000 * 1000

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
apiPrefix = '/api'

active_sessions = {}

cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'api', 'cache')
os.makedirs(cache_dir, exist_ok=True)

def get_cache_key(bounds):
    # Ensure bounds are properly formatted with full precision
    if not bounds or len(bounds) != 4:
        raise ValueError(f"Invalid bounds format: {bounds}")
    
    # Round to 6 decimal places (about 0.1m precision) to avoid floating point precision issues
    # but keep enough precision to distinguish different locations
    rounded_bounds = [round(float(b), 6) for b in bounds]
    bounds_str = json.dumps(rounded_bounds, sort_keys=True)
    cache_key = hashlib.md5(bounds_str.encode()).hexdigest()
    
    return cache_key

def get_cached_graph(bounds):
    cache_key = get_cache_key(bounds)
    cache_file = os.path.join(cache_dir, f'{cache_key}.json')
    
    if os.path.exists(cache_file):
        try:
            print(f"Cache hit! Using cache file: {cache_key}.json for bounds: {bounds}")
            with open(cache_file, 'r') as f:
                return json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Cache read error: {e}")
            pass
    else:
        print(f"Cache miss! No cache file found for bounds: {bounds} (cache key: {cache_key})")
    return None

def cache_graph(bounds, graph_dict):
    cache_key = get_cache_key(bounds)
    cache_file = os.path.join(cache_dir, f'{cache_key}.json')
    
    try:
        with open(cache_file, 'w') as f:
            json.dump(graph_dict, f)
        print(f"Graph cached successfully to: {cache_key}.json for bounds: {bounds}")
        print(f"Cache file size: {os.path.getsize(cache_file) / 1024 / 1024:.2f} MB")
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
        force_refresh = data.get('force_refresh', False)  # Allow forcing cache refresh
        
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
        
        MAX_AREA_KM2 = 100000
        if projected_area_km2 > MAX_AREA_KM2:
            return jsonify({
                'error': f'Area too large ({geographic_area_km2:.2f} km² geographic, {projected_area_km2:.2f} km² projected). Maximum allowed: {MAX_AREA_KM2} km². Please zoom in more on the map.',
                'area_km2': geographic_area_km2,
                'projected_area_km2': projected_area_km2,
                'max_allowed': MAX_AREA_KM2
            }), 400
        
        # Check cache unless force_refresh is True
        if not force_refresh:
            cached_result = get_cached_graph(bounds)
            if cached_result:
                print(f"Returning cached graph for bounds: {bounds}")
                return jsonify(cached_result)
        else:
            print(f"Force refresh requested - bypassing cache for bounds: {bounds}")
        
        print(f"Fetching NEW graph for bounds: {bounds} (Geographic area: {geographic_area_km2:.2f} km², Projected area: {projected_area_km2:.2f} km²)")
        print(f"Bounds details: min_lat={min_lat}, max_lat={max_lat}, min_lon={min_lon}, max_lon={max_lon}")
        start_time = time.time()
        
        location = Location(bounds=bounds)
        world = World(location, 0)

        graph = world.graph
        print(f"Graph created with {len(graph.nodes)} nodes and {len(graph.edges)} edges in {time.time() - start_time:.2f} seconds")
        
        result = graph.to_dict()
        cache_graph(bounds, result)
        
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
        
        if client_sid in active_sessions:
            active_sessions[client_sid].stop()
            del active_sessions[client_sid]
        
        eval_mode = data.get('eval_mode', False)
        mode_str = "evaluation" if eval_mode else "training"
        print(f"Starting DQN {mode_str} simulation for session {session_id} with {num_workers} workers")
        
        location = Location(bounds=bounds)
        world = World(location, num_workers)
        
        training_session = TrainingSession(world, session_id, num_workers, eval_mode=eval_mode)
        active_sessions[client_sid] = training_session
        
        initial_state = training_session.get_initial_state()
        emit('initial_state', initial_state)
        
        def run_training():
            update_interval = SIMULATION_UPDATE_INTERVAL
            last_update = time.time()
            
            training_session.start()
            
            while training_session.is_running:
                should_continue = training_session.step()
                
                if not should_continue:
                    break
                
                current_time = time.time()
                if current_time - last_update >= update_interval:
                    update_data = training_session.get_state_update()
                    socketio.emit('update', update_data, room=client_sid)
                    last_update = current_time
                
                time.sleep(SIMULATION_STEP_DELAY)
            
            final_state = training_session.get_state_update()
            final_state['progress'] = 1.0
            socketio.emit('final_state', final_state, room=client_sid)
            
            if client_sid in active_sessions:
                del active_sessions[client_sid]
            
            print(f"Training completed for session {session_id}")
            metrics = training_session.get_training_metrics()
            print(f"Final metrics: steps={metrics['step_count']}, reward={metrics['total_reward']}, epsilon={metrics['epsilon']:.4f}")
        
        thread = threading.Thread(target=run_training, daemon=True)
        thread.start()
        
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"Error in start_simulation: {str(e)}")
        print(f"Traceback: {error_trace}")
        emit('error', {'message': str(e), 'traceback': error_trace})


@socketio.on('stop_simulation')
def handle_stop_simulation(data=None):
    client_sid = request.sid
    
    if client_sid in active_sessions:
        session = active_sessions[client_sid]
        session.stop()
        print(f"Stopped simulation for client {client_sid}")
        emit('simulation_stopped', {'message': 'Simulation stopped'})
    else:
        emit('error', {'message': 'No active simulation to stop'})


@socketio.on('pause_simulation')
def handle_pause_simulation(data=None):
    client_sid = request.sid
    
    if client_sid in active_sessions:
        session = active_sessions[client_sid]
        session.pause()
        emit('simulation_paused', {'message': 'Simulation paused'})
    else:
        emit('error', {'message': 'No active simulation to pause'})


@socketio.on('resume_simulation')
def handle_resume_simulation(data=None):
    client_sid = request.sid
    
    if client_sid in active_sessions:
        session = active_sessions[client_sid]
        session.resume()
        emit('simulation_resumed', {'message': 'Simulation resumed'})
    else:
        emit('error', {'message': 'No active simulation to resume'})


@socketio.on('disconnect')
def handle_disconnect():
    client_sid = request.sid
    
    if client_sid in active_sessions:
        active_sessions[client_sid].stop()
        del active_sessions[client_sid]
        print(f"Client {client_sid} disconnected, stopped their simulation")

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)