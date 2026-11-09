"""IOWO D4's local Android backend. No website imports or shared server secrets.

The bundled reader is the website's real Bible Study module. This adapter owns
device login, resource setup, and the authenticated website connection only.
"""
import argparse
from contextlib import closing, contextmanager
import hashlib
import hmac
import importlib
import io
import json
import os
from pathlib import Path
import secrets
import shutil
import sqlite3
import sys
import threading
import time
from types import ModuleType, SimpleNamespace
from urllib.parse import urlsplit

import requests
from flask import Flask, Response, abort, current_app, g, jsonify, redirect, render_template, request, send_file, send_from_directory, session, url_for

APP_NAME = 'IOWO D4 Bible Study'
WEBSITE = 'https://iowod4tool.coresite.pro'
TERMS_VERSION = '2026-11-08'
SUPPORT_REMINDER_SECONDS = 3 * 24 * 60 * 60
_server = None
_application = None
_core = None
_owner = None
_maintenance_lock = threading.RLock()


def load_core(owner):
    """Replace only the website-wide dependencies; retain its study algorithms."""
    global _core, _owner
    _owner = owner
    if _core is not None:
        return _core
    resources = ModuleType('pastor_resources')
    resources.BIBLE_TRANSLATIONS_DRIVE_FOLDER_ID = ''
    resources.PASTOR_RESOURCES_DRIVE_FOLDER_ID = ''
    resources.GOOGLE_DRIVE_FOLDER_MIME = 'application/vnd.google-apps.folder'
    resources._appmod = lambda: getattr(current_app, '_offline_owner', _owner) if current_app else _owner
    def account_key():
        return getattr(g, 'device_profile', {}).get('user_key', '')
    resources.current_reader_user_key = account_key
    resources.is_resource_admin = lambda: False
    def remote_only(*args, **kwargs):
        raise ValueError('Library updates are included with app updates. Your offline resources are already installed.')
    resources.get_drive_session = remote_only
    resources.list_drive_folder = remote_only
    sys.modules['pastor_resources'] = resources
    runtime = ModuleType('runtime_config')
    @contextmanager
    def background_job_slot(path, name):
        with _maintenance_lock:
            yield
    runtime.background_job_slot = background_job_slot
    sys.modules['runtime_config'] = runtime
    _core = importlib.import_module('bible_study')
    return _core


def atomic_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    staging = path.with_suffix('.new')
    with staging.open('w', encoding='utf-8') as stream:
        json.dump(data, stream, ensure_ascii=False)
        stream.flush()
        os.fsync(stream.fileno())
    staging.replace(path)
    try:
        path.chmod(0o600)
    except OSError:
        pass


class DeviceState:
    def __init__(self, root, native=None):
        self.root, self.native = Path(root), native
        self.lock = threading.RLock()
        self.settings_path = self.root / 'settings.json'
        self.settings = json.loads(self.settings_path.read_text(encoding='utf-8')) if self.settings_path.is_file() else {}
        raw = str(native.readSession()) if native else ((self.root / 'desktop-session.json').read_text(encoding='utf-8') if (self.root / 'desktop-session.json').is_file() else '')
        try:
            self.profile = json.loads(raw) if raw else {}
        except (ValueError, TypeError):
            self.profile = {}
        self.setup = dict(running=False, completed=0, total=0, message='')

    def save_profile(self, profile):
        # Android uses AES-GCM with a key held by Android Keystore. Passwords
        # are never retained: only the revocable device token and display data.
        with self.lock:
            if self.native:
                self.native.writeSession(json.dumps(profile))
            else:
                atomic_json(self.root / 'desktop-session.json', profile)
            self.profile = profile

    def save_setting(self, **values):
        with self.lock:
            self.settings.update(values)
            atomic_json(self.settings_path, self.settings)


class WebsiteBridge:
    def __init__(self, profile):
        self.profile = profile
        base = profile.get('website', WEBSITE).rstrip('/')
        parsed = urlsplit(base)
        if parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment or parsed.path:
            raise ValueError('Use the HTTPS address of your IOWO website.')
        self.base = base

    def call(self, path, payload=None, authenticated=True):
        headers = {'Accept': 'application/json', 'User-Agent': 'IOWO-D4-Bible-Study/1.0'}
        if authenticated:
            headers['Authorization'] = 'Bearer ' + self.profile.get('token', '')
        try:
            response = requests.post(self.base + '/api/v1/bible-mobile/' + path,
                                     json=payload or {}, headers=headers, timeout=(10, 70), allow_redirects=False)
            if response.status_code == 404:
                raise ValueError('The website connection is not enabled yet. Ask the administrator to enable the supplied mobile integration.')
            if response.status_code == 401:
                raise ValueError('Sign in again to reconnect online backup. Your offline reading and saved notes remain available.')
            if len(response.content) > 2 * 1024 * 1024:
                raise ValueError('The website returned too much data.')
            data = response.json()
            if response.status_code >= 400 or not isinstance(data, dict):
                raise ValueError(data.get('error', 'The website could not complete this request.') if isinstance(data, dict) else 'Invalid website response.')
            return data
        except requests.RequestException:
            raise ValueError('An internet connection is needed for login and online backup. Your local notes are safe.') from None
        except requests.JSONDecodeError:
            raise ValueError('The website connection did not return a valid response.') from None


def file_hash(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def create_app(data_dir, web_dir, manifest_path, native=None, gate=None, bridge_factory=WebsiteBridge):
    root, web = Path(data_dir).resolve(), Path(web_dir).resolve()
    root.mkdir(parents=True, exist_ok=True)
    app = Flask(__name__, static_folder=str(web / 'static'), template_folder=str(web / 'templates'))
    key = root / 'session-signing.key'
    if not key.exists():
        key.write_bytes(secrets.token_bytes(32))
        try: key.chmod(0o600)
        except OSError: pass
    app.secret_key = key.read_bytes()
    app.config.update(SESSION_COOKIE_NAME='iowo_local_session', SESSION_COOKIE_HTTPONLY=True,
                      SESSION_COOKIE_SAMESITE='Strict', TEMPLATES_AUTO_RELOAD=not bool(native), MAX_CONTENT_LENGTH=1024 * 1024,
                      DATABASE=str(root / 'library/catalogue.db'), AI_DATABASE=str(root / 'library/study_library.db'),
                      BIBLE_STUDY_DATABASE=str(root / 'study/bible_study.db'),
                      BIBLE_ILLUSTRATIONS_DATABASE=str(root / 'study/sermon_illustrations.db'),
                      BIBLE_SERMON_NOTES_DATABASE=str(root / 'personal/sermon_notes.db'),
                      BIBLE_STUDY_LIBRARY_DATABASE=str(root / 'library/catalogue.db'),
                      SERMON_NOTES_DRIVE_SCRIPT_URL='website-managed', SERMON_NOTES_DRIVE_API_TOKEN='device-token-managed',
                      MOBILE_GATE=gate or secrets.token_urlsafe(32))
    state = DeviceState(root, native)
    manifest = json.loads(Path(manifest_path).read_text(encoding='utf-8'))
    app.device_state, app.resource_manifest = state, manifest
    app._offline_owner = SimpleNamespace(DATABASE=app.config['DATABASE'], AI_DATABASE=app.config['AI_DATABASE'])
    core = load_core(app._offline_owner)
    core.BASE_DIR = web
    original_pdf = getattr(core.sermon_notes_pdf, '_offline_original', core.sermon_notes_pdf)
    if native:
        def native_pdf(note):
            checked = core.validate_sermon_note(note)
            return bytes(native.createPdf(json.dumps(checked, ensure_ascii=False)))
        native_pdf._offline_original = original_pdf
        core.sermon_notes_pdf = native_pdf
    else:
        core.sermon_notes_pdf = original_pdf
    def bridge():
        return bridge_factory(state.profile)
    def drive_proxy(unused_app, user_key, action, **payload):
        if user_key != state.profile.get('user_key'):
            raise ValueError('The active account changed. Reopen your study workspace.')
        return bridge().call('drive', dict(action=action, **payload))
    core.sermon_notes_remote = drive_proxy
    original_sync = core.sync_sermon_notes
    # Avoid re-wrapping if a desktop test creates more than one app.
    original_sync = getattr(original_sync, '_offline_original', original_sync)
    def wait_for_website(progress):
        result = bridge().call('website-sync/start')
        for _ in range(1440):
            job = result.get('job', {})
            if not job.get('running'):
                if job.get('error'): raise ValueError(job['error'])
                return
            progress(message=job.get('message') or 'Preparing website backup', completed=job.get('completed', 0), total=job.get('total', 0))
            time.sleep(2)
            result = bridge().call('website-sync/status')
        raise ValueError('The website is still backing up notes. Your local notes are safe; retry later.')
    def connected_sync(unused_app, user_key, progress):
        wait_for_website(progress)
        result = original_sync(app, user_key, progress)
        wait_for_website(progress)
        return result
    connected_sync._offline_original = original_sync
    core.sync_sermon_notes = connected_sync

    @app.before_request
    def device_access():
        if request.endpoint == 'health': return None
        supplied = request.cookies.get('iowo_device_gate', '')
        if not hmac.compare_digest(supplied, app.config['MOBILE_GATE']):
            return jsonify(ok=False, error='Open this page inside IOWO D4 Bible Study.'), 403
        if request.headers.get('Origin') and request.headers['Origin'] != request.host_url.rstrip('/'):
            abort(403)
        g.device_profile = state.profile
        if state.profile:
            session['ao_logged_in'] = True
            session['ao_role'] = state.profile.get('role', 'pastor')
            session['ao_username'] = state.profile.get('username', '')
        else:
            for key in ('ao_logged_in', 'ao_role', 'ao_username', 'pastor_logged_in', 'pastor_username'):
                session.pop(key, None)
        if 'bible_study_csrf' not in session:
            session['bible_study_csrf'] = secrets.token_urlsafe(32)
        if request.path.startswith('/pastor-resources/'):
            if not state.profile or state.settings.get('agreement') != TERMS_VERSION or not state.settings.get('resources_ready'):
                return redirect(url_for('home'))
        if request.path.endswith('/api/sync') and request.method == 'POST':
            return jsonify(ok=False, error='Your study library is bundled with this app. Library updates arrive through app updates.'), 409
        return None

    @app.after_request
    def local_headers(response):
        response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['Referrer-Policy'] = 'no-referrer'
        response.headers['X-Frame-Options'] = 'DENY'
        if native and request.path.endswith('/api/notes/sync') and response.status_code == 200:
            native.beginSync('Backing up your sermon notes')
        return response

    @app.context_processor
    def mobile_context():
        return dict(app_name=APP_NAME, bible_startup_preload=True, device_profile=state.profile, mobile_csrf=session.get('bible_study_csrf', ''), resource_manifest=manifest)

    def require_write():
        if not hmac.compare_digest(request.headers.get('X-CSRF-Token', ''), session.get('bible_study_csrf', '')):
            abort(400)

    @app.post('/mobile/support/claim')
    def support_claim():
        require_write()
        if not state.profile or not state.settings.get('resources_ready'):
            return jsonify(ok=False, error='Open your prepared study workspace first.'), 403
        with state.lock:
            now = app.config.get('SUPPORT_REMINDER_CLOCK', time.time)()
            last = state.settings.get('support_last_shown', 0)
            last = float(last) if isinstance(last, (float, int)) else 0
            due = last <= 0 or now - last >= SUPPORT_REMINDER_SECONDS
            if due:
                state.save_setting(support_last_shown=now)
        return jsonify(ok=True, show=due, next_at=(now if due else last) + SUPPORT_REMINDER_SECONDS)

    @app.get('/healthz')
    def health():
        return jsonify(ok=True, app=APP_NAME)

    @app.get('/')
    def home():
        if state.settings.get('agreement') != TERMS_VERSION:
            return render_template('onboarding.html', stage='agreement')
        if not state.profile:
            return render_template('onboarding.html', stage='login')
        if not state.settings.get('resources_ready'):
            return render_template('onboarding.html', stage='setup')
        return redirect(url_for('bible_study.page'))

    @app.get('/mobile/runtime/static/fonts/<path:asset>')
    def tutorial_font(asset):
        if asset not in {'SpaceGrotesk-Variable.ttf', 'Lora-Variable.ttf'}:
            abort(404)
        return send_from_directory(Path(web_dir) / 'static' / 'fonts', asset)

    @app.get('/mobile/tutorials/')
    @app.get('/mobile/tutorials/<path:asset>')
    def mobile_tutorials(asset='index.html'):
        # Public within the device gate: help works before sign-in or setup.
        if asset not in {'index.html', 'tutorial.css', 'tutorial.js', 'screenshots.js'}:
            # Only bundled screenshot filenames may be read through this route.
            name = Path(asset).name
            if not (asset == 'images/' + name and name.endswith('.webp')
                    and all(char.isascii() and (char.isalnum() or char in '-.') for char in name)):
                abort(404)
        return send_from_directory(Path(web_dir).parent / 'tutorials', asset)

    @app.get('/mobile/privacy')
    def mobile_privacy():
        return render_template('privacy.html')

    @app.get('/mobile/splash')
    def mobile_splash():
        return render_template('splash.html')

    @app.get('/mobile/branding/splash.png')
    def branding_splash():
        return send_file(Path(manifest_path).resolve().parent / 'branding/splash.png', mimetype='image/png')

    @app.get('/mobile/branding/icon.png')
    def branding_icon():
        return send_file(Path(manifest_path).resolve().parent / 'branding/icon.png', mimetype='image/png')

    @app.get('/about-publisher')
    @app.get('/about-developer')
    def about():
        return render_template('about.html', publisher_return_url=url_for('mobile_splash') if request.args.get('return') == 'splash' else url_for('home'))

    @app.post('/mobile/agree')
    def agree():
        require_write()
        if (request.get_json(silent=True) or {}).get('accepted') is not True:
            return jsonify(ok=False, error='Please accept the agreement to continue.'), 400
        state.save_setting(agreement=TERMS_VERSION)
        return jsonify(ok=True)

    @app.post('/mobile/login')
    def login():
        require_write()
        if notes_job_running(): return jsonify(ok=False, error='Let the current backup finish before changing accounts.'), 409
        if state.settings.get('agreement') != TERMS_VERSION: abort(403)
        data = request.get_json(silent=True) or {}
        username, password = data.get('username', ''), data.get('password', '')
        if not isinstance(username, str) or not isinstance(password, str) or not username.strip() or not password or len(username) > 200 or len(password) > 500:
            return jsonify(ok=False, error='Enter your website username and password.'), 400
        try:
            result = bridge_factory(dict(website=data.get('website', WEBSITE))).call('login',
                dict(username=username.strip(), password=password, device_name='IOWO D4 Android'), authenticated=False)
            profile = result.get('profile', {})
            if not result.get('ok') or not isinstance(profile, dict) or not profile.get('user_key') or not profile.get('token'):
                raise ValueError(result.get('error', 'The website could not confirm your account.'))
            profile['website'] = data.get('website', WEBSITE).rstrip('/')
            state.save_profile(profile)
            return jsonify(ok=True)
        except ValueError as error:
            return jsonify(ok=False, error=str(error)), 400

    @app.post('/mobile/logout')
    def logout():
        require_write()
        if notes_job_running(): return jsonify(ok=False, error='Let the current backup finish before signing out.'), 409
        state.save_profile({})
        session.clear()
        return jsonify(ok=True)

    def notes_job_running():
        key = (str(app.config['BIBLE_SERMON_NOTES_DATABASE']), state.profile.get('user_key', ''))
        with core._notes_jobs_lock:
            return bool(core._notes_jobs.get(key, {}).get('running'))

    def required_setup_bytes():
        if native: return int(native.requiredSetupBytes())
        return 256 * 1024 * 1024 + sum(entry['bytes'] for entry in manifest['files']
            if not (root / entry['path']).is_file() or (root / entry['path']).stat().st_size != entry['bytes'])

    @app.get('/mobile/storage')
    def storage():
        available = shutil.disk_usage(root).free
        required = required_setup_bytes()
        return jsonify(ok=True, free_bytes=available, required_bytes=required, resource_bytes=manifest['resource_bytes'],
                       sufficient=available >= required)

    def install_resources():
        try:
            if native:
                native.installResources()
            else:
                project = Path(manifest_path).resolve().parents[4]
                for i, entry in enumerate(manifest['files']):
                    destination = root / entry['path']
                    destination.parent.mkdir(parents=True, exist_ok=True)
                    if destination.is_file():
                        if destination.stat().st_size == entry['bytes'] and file_hash(destination) == entry['sha256']:
                            continue
                        raise ValueError('An existing library needs recovery before setup. Your saved data was kept.')
                    staging = destination.with_suffix(destination.suffix + '.installing')
                    shutil.copyfile(project / entry['project_path'], staging)
                    if file_hash(staging) != entry['sha256']: raise ValueError('A bundled resource could not be verified.')
                    staging.replace(destination)
                    state.setup.update(completed=i+1, total=len(manifest['files']), message='Preparing offline study resources')
            state.save_setting(resources_ready=True, resource_version=manifest['resource_version'])
            state.setup.update(running=False, message='Your offline library is ready.')
        except Exception as error:
            state.setup.update(running=False, error=str(error), message='Setup did not finish. Your account and notes are safe; retry setup.')

    @app.post('/mobile/setup')
    def setup():
        require_write()
        if not state.profile or state.settings.get('agreement') != TERMS_VERSION: abort(403)
        if state.settings.get('resources_ready'): return jsonify(ok=True, ready=True)
        with state.lock:
            if not state.setup.get('running'):
                if shutil.disk_usage(root).free < required_setup_bytes():
                    return jsonify(ok=False, error='There is not enough free space for the offline library.'), 400
                state.setup = dict(running=True, completed=0, total=len(manifest['files']), message='Preparing your offline library')
                threading.Thread(target=install_resources, name='offline-library-setup', daemon=True).start()
        return jsonify(ok=True, **state.setup)

    @app.get('/mobile/setup/status')
    def setup_status():
        progress = dict(state.setup)
        if native and progress.get('running'):
            try: progress.update(json.loads(str(native.resourceProgress())))
            except (ValueError, TypeError): pass
        return jsonify(ok=True, ready=bool(state.settings.get('resources_ready')), **progress)

    core.register_bible_study_routes(app)
    # Endpoints referenced by the unchanged Bible Study and icon templates.
    app.add_url_rule('/start', 'splash', lambda: redirect(url_for('home')))
    app.add_url_rule('/library', 'pastor_resources', lambda: redirect(url_for('bible_study.page')))

    @app.get('/pastor-resources/my-library')
    def saved_library():
        if not state.profile or not state.settings.get('resources_ready'): return redirect(url_for('home'))
        items = core.bible_personal_library(app, state.profile['user_key'])
        for item in items['bookmarks']:
            item.setdefault('kind', 'bookmark')
            item.setdefault('selected_text', item.get('label', ''))
        return render_template('saved.html', items=items['annotations']+items['bookmarks'])

    @app.errorhandler(ValueError)
    def validation_error(error):
        return jsonify(ok=False, error=str(error)), 400

    return app


def start_android(native, data_dir, web_dir, manifest_path):
    global _server, _application
    if _server is None:
        from werkzeug.serving import make_server
        _application = create_app(data_dir, web_dir, manifest_path, native=native)
        # Keep the origin across process restarts: WebView drafts and display
        # preferences use localStorage, which is scoped to the server's port.
        # The installation chooses a random port once; the access gate rotates.
        preferred = _application.device_state.settings.get('backend_port', 0)
        if type(preferred) is not int or not 1024 <= preferred <= 65535: preferred = 0
        try:
            _server = make_server('127.0.0.1', preferred, _application, threaded=True)
        except SystemExit:
            if not preferred: raise
            _server = make_server('127.0.0.1', 0, _application, threaded=True)
        _application.device_state.save_setting(backend_port=_server.server_port)
        threading.Thread(target=_server.serve_forever, name='offline-study-server', daemon=True).start()
    return json.dumps(dict(url='http://127.0.0.1:' + str(_server.server_port), gate=_application.config['MOBILE_GATE']))


def sync_status():
    if not _application or not _application.device_state.profile: return json.dumps(dict(running=False))
    key = (_application.config['BIBLE_SERMON_NOTES_DATABASE'], _application.device_state.profile['user_key'])
    with _core._notes_jobs_lock:
        return json.dumps(dict(_core._notes_jobs.get(key, dict(running=False))))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the Android study engine on desktop, without an APK.')
    parser.add_argument('--project', type=Path, default=Path(__file__).resolve().parents[4])
    parser.add_argument('--port', type=int, default=8765)
    args = parser.parse_args()
    project = args.project.resolve()
    app = create_app(project / '.desktop-data', project / 'app/src/main/assets/runtime', project / 'app/src/main/assets/resource-manifest.json')
    from werkzeug.serving import make_server
    server = make_server('127.0.0.1', args.port, app, threaded=True)
    print('Open this one-time local preview URL: http://127.0.0.1:' + str(args.port) + '/preview?gate=' + app.config['MOBILE_GATE'], flush=True)
    @app.get('/preview')
    def preview():
        if not hmac.compare_digest(request.args.get('gate', ''), app.config['MOBILE_GATE']): abort(403)
        response = redirect(url_for('mobile_splash'))
        response.set_cookie('iowo_device_gate', app.config['MOBILE_GATE'], httponly=True, samesite='Strict')
        return response
    # Only the explicit desktop bootstrap route may bypass its own cookie gate.
    app.before_request_funcs[None].insert(0, lambda: None)
    original_gate = app.before_request_funcs[None][1]
    app.before_request_funcs[None][1] = lambda: None if request.endpoint == 'preview' else original_gate()
    server.serve_forever()
