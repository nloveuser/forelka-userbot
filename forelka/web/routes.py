"""
Web routes for Forelka Userbot
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
import json
import os

web_routes = Blueprint('web_routes', __name__)


@web_routes.route('/')
@login_required
def dashboard():
    """Main dashboard"""
    return render_template('dashboard.html')


@web_routes.route('/accounts')
@login_required
def accounts():
    """Accounts management page"""
    return render_template('accounts.html')


@web_routes.route('/modules')
@login_required
def modules():
    """Modules management page"""
    return render_template('modules.html')


@web_routes.route('/settings')
@login_required
def settings():
    """Settings page"""
    return render_template('settings.html')


@web_routes.route('/logs')
@login_required
def logs():
    """Logs viewer page"""
    return render_template('logs.html')


@web_routes.route('/api/accounts', methods=['GET', 'POST', 'DELETE'])
@login_required
def api_accounts():
    """API endpoint for account management"""
    from ..core.database import DatabaseManager
    from ..core.config import ConfigManager
    
    db = DatabaseManager(ConfigManager().get("database_path", "forelka.db"))
    
    if request.method == 'GET':
        try:
            accounts = db.get_all_accounts()
            return jsonify({'success': True, 'accounts': accounts})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            user_id = data.get('user_id')
            api_id = data.get('api_id')
            api_hash = data.get('api_hash')
            prefix = data.get('prefix', '.')
            
            if not all([user_id, api_id, api_hash]):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            account_id = db.add_account(user_id, api_id, api_hash, prefix)
            return jsonify({'success': True, 'account_id': account_id})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            data = request.get_json()
            account_id = data.get('account_id')
            
            if not account_id:
                return jsonify({'success': False, 'error': 'Account ID required'}), 400
            
            db.remove_account(account_id)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


@web_routes.route('/api/modules', methods=['GET'])
@login_required
def api_modules():
    """API endpoint for module management"""
    from ..core.bot import ForelkaBot
    
    try:
        bot = ForelkaBot()
        modules = bot.modules.get_all_modules()
        return jsonify({'success': True, 'modules': modules})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@web_routes.route('/api/logs', methods=['GET'])
@login_required
def api_logs():
    """API endpoint for log viewing"""
    try:
        log_file = 'forelka.log'
        if not os.path.exists(log_file):
            return jsonify({'success': True, 'logs': []})
        
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Return last 1000 lines
            logs = [line.strip() for line in lines[-1000:]]
            return jsonify({'success': True, 'logs': logs})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@web_routes.route('/api/config', methods=['GET', 'POST'])
@login_required
def api_config():
    """API endpoint for configuration management"""
    from ..core.config import ConfigManager
    
    config = ConfigManager()
    
    if request.method == 'GET':
        try:
            return jsonify({
                'success': True,
                'config': {
                    'database_path': config.get('database_path'),
                    'log_level': config.get('log_level'),
                    'web_interface': config.get_web_config(),
                    'inline_bot': config.get_inline_bot_config(),
                    'modules': config.get_modules_config()
                }
            })
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            data = request.get_json()
            config.update(data)
            return jsonify({'success': True})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)}), 500


def setup_routes(app):
    """Setup all routes"""
    app.register_blueprint(web_routes)