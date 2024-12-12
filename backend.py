from flask import Flask, request, jsonify
from flask_cors import CORS
import scratchattach as scratch3
import time

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Store session globally (not the best practice for production, but works for demo)
current_session = None
current_user = None

# In the login route, modify the stats handling:
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        global current_session, current_user
        current_session = scratch3.login(username, password)
        current_user = scratch3.get_user(username)
        
        stats = current_user.stats()
        # Fix negative values
        stats = {
            'followers': max(0, stats.get('followers', 0)),
            'following': max(0, stats.get('following', 0)),
            'views': max(0, stats.get('views', 0))
        }
        
        return jsonify({
            'success': True,
            'username': username,
            'id': current_user.id,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/projects', methods=['GET'])
def get_projects():
    try:
        if not current_user:
            return jsonify({'success': False, 'error': 'Not logged in'})
        
        projects = current_user.projects()
        project_list = []
        
        for project in projects:
            project_list.append({
                'title': project.title,
                'id': project.id
            })
        
        return jsonify({
            'success': True,
            'projects': project_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/project/<project_id>/comment', methods=['POST'])
def post_project_comment(project_id):
    try:
        if not current_session:
            return jsonify({'success': False, 'error': 'Not logged in'})
        
        data = request.json
        comment = data.get('comment')
        
        project = current_session.connect_project(project_id)
        project.post_comment(comment)
        
        return jsonify({
            'success': True,
            'message': 'Comment posted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

@app.route('/logout', methods=['POST'])
def logout():
    global current_session, current_user
    current_session = None
    current_user = None
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True, port=5000)