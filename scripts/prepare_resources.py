"""Prepare public offline resources. Never imports or writes the live website.

Run with the existing website virtualenv, which already has the reading dependencies.
All source SQLite connections are read-only. Personal notes/accounts are never copied.
"""
import argparse
import ast
from contextlib import closing
import hashlib
import importlib
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import tempfile

PROJECT = Path(__file__).resolve().parents[1]
PYTHON = PROJECT / 'app/src/main/python'
ASSETS = PROJECT / 'app/src/main/assets'
WEB = ASSETS / 'runtime'


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def readonly(path):
    return closing(sqlite3.connect(path.resolve().as_uri() + '?mode=ro', uri=True, timeout=30))


def snapshot(source, target, strip_personal=False):
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.is_file():
        print('Keeping prepared snapshot:', target.name, flush=True)
        return
    temporary = target.with_suffix('.staging')
    with readonly(source) as origin, closing(sqlite3.connect(temporary)) as output:
        origin.backup(output)
        if strip_personal:
            output.execute('PRAGMA foreign_keys=OFF')
            output.execute('PRAGMA secure_delete=ON')
            for (table,) in output.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall():
                columns = {row[1] for row in output.execute('PRAGMA table_info("' + table.replace('"', '""') + '")')}
                if 'user_key' in columns:
                    output.execute('DELETE FROM "' + table.replace('"', '""') + '"')
            output.commit()
            # Rebuild free pages too: deleted private marks must not survive in
            # the shared file's SQLite freelist or unused page space.
            output.execute('VACUUM')
        assert output.execute('PRAGMA quick_check').fetchall() == [('ok',)]
    temporary.replace(target)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--website', type=Path, required=True)
    parser.add_argument('--skip-cache', action='store_true', help='Only for development; production must include prepared reader caches.')
    args = parser.parse_args()
    website = args.website.resolve()
    if website == PROJECT or not (website / 'bible_study.py').is_file():
        raise SystemExit('Choose the existing website folder as --website.')
    PYTHON.mkdir(parents=True, exist_ok=True)
    (WEB / 'templates').mkdir(parents=True, exist_ok=True)
    (WEB / 'static').mkdir(parents=True, exist_ok=True)
    source = (website / 'bible_study.py').read_text(encoding='utf-8')
    # Make the derived-cache keys portable from this preparation machine to Android.
    for before, after in [
        ('[_CATALOGUE_PARSER_REVISION,str(Path(path).resolve()),documents]', '[_CATALOGUE_PARSER_REVISION,"iowo-d4-library-v1",documents]'),
        ('[1,str(Path(path).resolve()),document_id,fingerprint]', '[1,"iowo-d4-library-v1",document_id,fingerprint]'),
    ]:
        if source.count(before) != 1:
            raise SystemExit('The website cache-key implementation changed; review the Android adapter.')
        source = source.replace(before, after)
    (PYTHON / 'bible_study.py').write_text(source, encoding='utf-8')
    template = (website / 'templates/bible_study.html').read_text(encoding='utf-8')
    template = template.replace('Bible Study — District 4 Tool', 'Bible Study — IOWO D4')
    style = re.search(r'<link rel="stylesheet" href="\{\{ url_for\(\'static\', filename=\'bible_study.css\'.*?\}\}">', template)
    if style is None:
        raise SystemExit('Review the Android Bible Study stylesheet placement for the updated website.')
    template = template.replace(style[0], '')
    template = template.replace('{% block content %}', '{% block page_styles %}' + style[0] + '{% endblock %}\n{% block content %}', 1)
    # Shared resources update with the Android distribution. Keep the genuine
    # developer sermon converter, but remove the website's Drive library importer.
    template = re.sub(r'      \{% if bible_study_admin %\}<fieldset class="bs-sync-actions">.*?</fieldset>\{% endif %\}', '', template, flags=re.S)
    original = '      <a href="{{ url_for(\'pastor_resources\') }}">&larr; Back to Library</a>'
    if template.count(original) != 1:
        raise SystemExit('Review the Android reading-settings account controls for the updated website.')
    template = template.replace(original, '''      <fieldset><legend>Account</legend>
        <p>{{ device_profile.get('name') or device_profile.get('username') }}</p>
        <button type="button" id="mobileSignOut">Sign out on this device</button>
      </fieldset>''')
    (WEB / 'templates/bible_study.html').write_text(template, encoding='utf-8')
    shutil.copy2(website / 'templates/ui_icons.html', WEB / 'templates/ui_icons.html')
    for name in ['bible_study.js', 'bible_study.css', 'styles.css', 'visual_upgrade.css', 'glass_theme.css']:
        shutil.copy2(website / 'static' / name, WEB / 'static' / name)
    reader = (WEB / 'static/bible_study.js').read_text(encoding='utf-8')
    original = 'function notesDownload(){if(!notesPDFUrl)return;'
    if reader.count(original) != 1:
        raise SystemExit('Review the native PDF-download adapter for the updated website.')
    reader = reader.replace(original, original + 'if(window.IOWOAndroid&&window.iowoExportFile){window.iowoExportFile(notesPDF,false);return;}')
    original = 'const data=await api(apiBase+"/notes?"+new URLSearchParams({q:query}));notesItems=data.notes||[];notesLoaded=true;'
    if reader.count(original) != 1:
        raise SystemExit('Review the Android notes progress-resume adapter for the updated website.')
    reader = reader.replace(original,
        'const firstLoad=!notesLoaded;' + original + '\n        if(firstLoad){const current=await api(apiBase+"/notes/job");if(current.job.running){clearTimeout(notesJobTimer);notesRenderJob(current.job);notesJobTimer=setTimeout(notesPollJob,500);}}')
    (WEB / 'static/bible_study.js').write_text(reader, encoding='utf-8')
    for folder in ['fonts', 'icons', 'img']:
        shutil.copytree(website / 'static' / folder, WEB / 'static' / folder, dirs_exist_ok=True)
    for name in ['pijeme.png', 'bernard.png']:
        target = WEB / 'static/developers' / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(website / 'static/developers' / name, target)
    for name in ['For icon.png', 'For Splash Screen.png']:
        target = ASSETS / 'branding' / ('icon.png' if name == 'For icon.png' else 'splash.png')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(PROJECT / 'Images' / name, target)
    drawable = PROJECT / 'app/src/main/res/drawable-nodpi'
    drawable.mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROJECT / 'Images/For icon.png', drawable / 'app_icon.png')
    shutil.copytree(PROJECT / 'about-developer', ASSETS / 'about-developer', dirs_exist_ok=True)
    about = (PROJECT / 'about-developer/index.html').read_text(encoding='utf-8')
    about = about.replace('<title>About Developer</title>', '<title>About Publisher · IOWO D4 Bible Study</title>')
    about = about.replace('The People Behind <span>the Tool</span>', 'The People Behind <span>IOWO D4 Bible Study</span>')
    publisher_type = '''<style>
@font-face{font-family:PublisherDisplay;src:url('../runtime/static/fonts/Lora-Variable.ttf') format('truetype');font-weight:400 700;font-display:swap}
@font-face{font-family:PublisherUI;src:url('../runtime/static/fonts/SpaceGrotesk-Variable.ttf') format('truetype');font-weight:300 700;font-display:swap}
body .dev-tech-page{font-family:PublisherUI,sans-serif}
body .dev-tech-page :is(h1,h2,h3){font-family:PublisherDisplay,serif;letter-spacing:-.035em}
</style>'''
    about = about.replace('</head>', publisher_type + '</head>')
    (ASSETS / 'about-developer/index.html').write_text(about, encoding='utf-8')
    about = about.replace('src="images/', 'src="/static/developers/')
    about = about.replace('../runtime/static/fonts/', '/static/fonts/')
    about = about.replace('<body>', '<body><a class="dev-back" href="{{ publisher_return_url }}" style="position:relative;z-index:5;display:block;padding:16px;color:#aaffdf">← Back to app</a>')
    (WEB / 'templates/about.html').write_text(about, encoding='utf-8')

    core = PROJECT / 'study_core/src/main/assets/study/bible_study.db'
    illustrations = PROJECT / 'study_illustrations/src/main/assets/study/sermon_illustrations.db'
    library = PROJECT / 'study_library/src/main/assets/library/study_library.db'
    catalog = library.with_name('catalogue.db')
    print('Snapshotting shared Bible resources (live notes are excluded).', flush=True)
    snapshot(website / 'bible_study_data/bible_study.db', core, strip_personal=True)
    snapshot(website / 'bible_study_data/sermon_illustrations.db', illustrations, strip_personal=True)
    audit = json.loads((PROJECT / 'storage-audit.json').read_text(encoding='utf-8'))
    ids = sorted(item['id'] for item in audit['selected_library_documents'])
    marks = ','.join('?' for _ in ids)
    library.parent.mkdir(parents=True, exist_ok=True)
    if not library.is_file():
        print('Exporting the public commentary and sermon sources.', flush=True)
        temporary = library.with_suffix('.staging')
        with readonly(website / 'ai_index.db') as source_db, closing(sqlite3.connect(temporary, uri=True)) as output:
            output.execute('ATTACH DATABASE ? AS original', ((website / 'ai_index.db').as_uri() + '?mode=ro',))
            for table, key in [('pij_library_documents', 'id'), ('pij_library_chunks', 'document_id'), ('pij_library_source_formats', 'document_id')]:
                output.execute(source_db.execute('SELECT sql FROM sqlite_master WHERE name=?', (table,)).fetchone()[0])
                output.execute('INSERT INTO ' + table + ' SELECT * FROM original.' + table + ' WHERE ' + key + ' IN (' + marks + ')', ids)
            for (sql,) in source_db.execute("SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name IN ('pij_library_documents','pij_library_chunks') AND sql IS NOT NULL"):
                output.execute(sql)
            output.commit()
            assert output.execute('PRAGMA quick_check').fetchall() == [('ok',)]
        temporary.replace(library)
    if not catalog.is_file():
        with readonly(library) as index, closing(sqlite3.connect(catalog)) as output:
            output.execute('CREATE TABLE pastor_library_books(id INTEGER PRIMARY KEY,is_active INTEGER,is_hidden INTEGER)')
            output.execute('CREATE TABLE pastor_library_files(id INTEGER PRIMARY KEY,drive_file_id TEXT,book_id INTEGER,is_active INTEGER,is_duplicate INTEGER)')
            for identifier, file_id, book_id, source_id in index.execute('SELECT id,drive_file_id,book_id,source_file_id FROM pij_library_documents'):
                output.execute('INSERT OR IGNORE INTO pastor_library_books VALUES (?,1,0)', (book_id,))
                output.execute('INSERT INTO pastor_library_files VALUES (?,?,?,1,0)', (source_id, file_id, book_id))
            output.commit()
    sys.path.insert(0, str(PYTHON))
    from offline_app import load_core
    from types import SimpleNamespace
    owner = SimpleNamespace(DATABASE=str(catalog), AI_DATABASE=str(library))
    study = load_core(owner)
    study.BASE_DIR = WEB
    if not args.skip_cache:
        print('Preparing portable, offline reader catalogues.', flush=True)
        print(json.dumps(study.prepare_reader_catalogues(library)), flush=True)
    manifest_files = []
    for pack in ['study_core', 'study_library', 'study_illustrations']:
        assets = PROJECT / pack / 'src/main/assets'
        for file in sorted(path for path in assets.rglob('*') if path.is_file() and path.suffix not in ('.tmp', '.staging')):
            if file.name.endswith(('-wal','-shm','-journal','.lock')):
                if file.name.endswith('-wal') and file.stat().st_size:
                    raise SystemExit('Checkpoint and close the prepared resource database before packaging: ' + str(file))
                continue
            manifest_files.append(dict(path=file.relative_to(assets).as_posix(), project_path=file.relative_to(PROJECT).as_posix(),
                                       bytes=file.stat().st_size, sha256=digest(file)))
    total = sum(file['bytes'] for file in manifest_files)
    manifest = dict(schema_version=1, app_name='IOWO D4 Bible Study', resource_version='2026.11.08.1',
                    files=manifest_files, resource_bytes=total, setup_free_bytes=total + 256 * 1024 * 1024,
                    public_library_documents=len(ids), includes_personal_notes=False, caches_prepared=not args.skip_cache,
                    source_commit='bf5e725', final_android_installed_size='Measure after the later APK/AAB build.')
    (ASSETS / 'resource-manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'prepared': True, 'resource_bytes': total, 'files': len(manifest_files), 'apk_generated': False}), flush=True)


if __name__ == '__main__':
    main()
