from flask import Flask, jsonify, abort
from flask_cors import CORS
from pathlib import Path
import json

app = Flask(__name__)
CORS(app)                                                                   # разрешаем доступ с фронта
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR.joinpath('..', 'data', 'projects').resolve()            # путь к данным можно вынести в .env потом
print("DATA_DIR =", DATA_DIR)

def read_json_file(path: Path):
    try:
        with path.open('r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error reading JSON {path}: {e}")
        return None

def iter_project_dirs():
    if not DATA_DIR.exists() or not DATA_DIR.is_dir():
        print("Projects directory not found:", DATA_DIR)
        return
    for entry in sorted(DATA_DIR.iterdir()):
        if entry.is_dir():
            yield entry

def load_project_minimal(project_path: Path):
    pj_file = project_path.joinpath('project.json')
    if not pj_file.exists():
        print("Missing project.json in", project_path)
        return None
    data = read_json_file(pj_file)
    if not isinstance(data, dict):
        return None
    result = {}
    if 'id' in data:
        result['id'] = data['id']
    if 'name' in data:
        result['name'] = data['name']
    loc = data.get('location') or data.get('coords') or data.get('coordinates')
    if isinstance(loc, dict) and 'lat' in loc and 'lon' in loc:
        result['location'] = {'lat': loc['lat'], 'lon': loc['lon']}
    if 'category' in data:
        result['category'] = data['category']
    return result

def load_full_project(project_path: Path):
    pj_file = project_path.joinpath('project.json')
    if not pj_file.exists():
        return None
    data = read_json_file(pj_file)
    if not isinstance(data, dict):
        return None
    return data

def get_all_projects_minimal():
    results = []
    for d in iter_project_dirs():
        mini = load_project_minimal(d)
        if mini:
            results.append(mini)
    return results

def find_project_by_id(project_id: str):                                    # при росте числа файлов перейти на нормальную бд
    for d in iter_project_dirs():
        full = load_full_project(d)
        if isinstance(full, dict) and full.get('id') == project_id:
            return full
    return None


# API Endpoints
@app.route('/api/ping', methods=['GET'])
def ping():
    return jsonify({"status": "success", "message": "Backend is online!", "data": None})

@app.route('/api/projects', methods=['GET'])
def api_projects():
    projects = get_all_projects_minimal()
    return jsonify(projects)

@app.route('/api/projects/<project_id>', methods=['GET'])
def api_project_detail(project_id):
    proj = find_project_by_id(project_id)
    if proj is None:
        return jsonify({"error": "Project not found"}), 404
    return jsonify(proj)

if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5000, debug=True)
