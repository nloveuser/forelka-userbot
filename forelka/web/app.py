"""
Flask web application for Forelka Userbot
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
from datetime import datetime

from ..core.config import ConfigManager
from ..core.database import DatabaseManager
from ..utils.helpers import get_system_info


class WebUser(UserMixin):
    """User class for Flask-Login"""
    def __init__(self, id):
        self.id = id


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Load configuration
    config = ConfigManager()
    web_config = config.get_web_config()
    
    app.config.update(
        SECRET_KEY=web_config.get('secret_key', 'forelka-secret-key-change-me'),
        DEBUG=False,
        HOST=web_config.get('host', '127.0.0.1'),
        PORT=web_config.get('port', 8080)
    )
    
    # Initialize extensions
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'
    
    # Initialize database
    db = DatabaseManager(config.get("database_path", "forelka.db"))
    
    @login_manager.user_loader
    def load_user(user_id):
        return WebUser(user_id) if user_id == "admin" else None
    
    # Routes
    @app.route('/')
    @login_required
    def dashboard():
        """Main dashboard"""
        return render_template('dashboard.html')
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """Login page"""
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            
            # Simple authentication (in production, use proper auth)
            if username == 'admin' and password == 'admin':  # Change this!
                user = WebUser('admin')
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid credentials')
        
        return render_template('login.html')
    
    @app.route('/logout')
    @login_required
    def logout():
        """Logout"""
        logout_user()
        return redirect(url_for('login'))
    
    @app.route('/api/status')
    @login_required
    def api_status():
        """Get bot status"""
        try:
            # This would need to be connected to the actual bot instance
            # For now, return mock data
            return jsonify({
                'status': 'running',
                'accounts': 1,
                'modules': 5,
                'uptime': '2 hours',
                'system_info': get_system_info()
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/accounts')
    @login_required
    def api_accounts():
        """Get all accounts"""
        try:
            accounts = db.get_all_accounts()
            return jsonify(accounts)
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/modules')
    @login_required
    def api_modules():
        """Get all modules"""
        try:
            # This would need to be connected to the actual bot instance
            # For now, return mock data
            return jsonify([
                {'name': 'help', 'status': 'enabled', 'version': '1.0'},
                {'name': 'ping', 'status': 'enabled', 'version': '1.0'},
                {'name': 'owner', 'status': 'enabled', 'version': '1.0'},
                {'name': 'prefix', 'status': 'enabled', 'version': '1.0'},
                {'name': 'alias', 'status': 'enabled', 'version': '1.0'}
            ])
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/logs')
    @login_required
    def api_logs():
        """Get recent logs"""
        try:
            log_file = 'forelka.log'
            if os.path.exists(log_file):
                with open(log_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[-100:]  # Last 100 lines
                    return jsonify({'logs': lines})
            else:
                return jsonify({'logs': []})
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return app


def run_web_server():
    """Run the web server"""
    app = create_app()
    config = ConfigManager()
    web_config = config.get_web_config()
    
    if web_config.get('enabled', True):
        print(f"🌐 Starting web interface at http://{web_config['host']}:{web_config['port']}")
        app.run(
            host=web_config['host'],
            port=web_config['port'],
            debug=False
        )
    else:
        print("🌐 Web interface is disabled")