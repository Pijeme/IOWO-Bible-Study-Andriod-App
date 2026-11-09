"""Capture the real offline reader with fictional data for bundled help.

Run with .tools/test-env/Scripts/python.exe. No phone, live account or website
is accessed. WebP files are shared between topics; arrows remain tiny vectors.
"""
from contextlib import closing
import hashlib
import io
import json
from pathlib import Path
import sqlite3
import sys
import threading
import time

from PIL import Image
from playwright.sync_api import sync_playwright
from werkzeug.serving import make_server, WSGIRequestHandler

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / 'tests'))
from test_offline import prepared_app, PROFILE, API


class QuietHandler(WSGIRequestHandler):
    def log(self, *args, **kwargs):
        pass


def main():
    app = prepared_app(PROJECT / '.test-data/tutorial-capture')
    app.device_state.save_profile(dict(PROFILE, user_key='pastor:tutorial-capture',
                                       username='tutorial', name='Tutorial account', can_convert=True))
    app.device_state.save_setting(support_last_shown=time.time())
    notes_path = Path(app.config['BIBLE_SERMON_NOTES_DATABASE'])
    if notes_path.exists():
        with closing(sqlite3.connect(notes_path)) as db:
            db.execute("DELETE FROM sermon_notes WHERE user_key=?", ('pastor:tutorial-capture',))
            db.commit()

    server = make_server('127.0.0.1', 0, app, threaded=True, request_handler=QuietHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    url = 'http://127.0.0.1:' + str(server.server_port)
    output = PROJECT / 'app/src/main/assets/tutorials'
    images = output / 'images'
    images.mkdir(exist_ok=True)
    manifest, hashes = {}, {}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(viewport=dict(width=390, height=844),
                                          device_scale_factor=1.5, is_mobile=True, has_touch=True)
            context.add_cookies([dict(name='iowo_device_gate', value='test-gate', url=url)])
            page = context.new_page()
            page.add_init_script("window.IOWOAndroid={tutorialActive:()=>true,copyText:()=>{},shareText:()=>{}};")
            def local_only(route):
                if route.request.url.startswith(url + '/'):
                    route.continue_()
                else:
                    raise AssertionError('Capture tried an external request: ' + route.request.url)
            page.route('**/*', local_only)
            page.set_default_timeout(12000)

            def ready():
                page.wait_for_function('window.iowoStudyReady===true', timeout=45000)
                page.evaluate('document.fonts.ready')

            def click(selector):
                if selector in {'#bsWordTab','#bsConcordanceTab','#bsCommentaryTab','#bsSermonTab','#bsIllustrationsTab'}:
                    page.locator('#bsLayoutMode').select_option('study')
                if selector in {'#bsReaderTab','#bsBookStudyTab','#bsNotesTab'}:
                    page.locator('#bsLayoutMode').select_option('bible')
                page.locator(selector).first.click()
                if selector in {'#bsWordTab','#bsConcordanceTab','#bsCommentaryTab','#bsSermonTab','#bsIllustrationsTab'}:
                    page.evaluate("document.querySelector('#bsStudy').scrollTop=0")
                if selector in {'#bsReaderTab','#bsBookStudyTab','#bsNotesTab'}:
                    page.evaluate("document.querySelector('#bsBible').scrollTop=0")

            def reset():
                page.goto(url + '/pastor-resources/bible-study')
                ready()

            def dismiss():
                page.evaluate("document.querySelectorAll('dialog[open]').forEach(d=>d.close());getSelection().removeAllRanges();document.dispatchEvent(new Event('selectionchange'))")

            def capture(name, topics, scope=None):
                """Capture visible controls and retain their positions for vector arrows."""
                page.evaluate('document.fonts.ready')
                page.wait_for_timeout(100)
                bounds = {}
                for topic, marks in topics.items():
                    bounds[topic] = []
                    for selector, label in marks:
                        locator = page.locator(selector).first
                        assert locator.is_visible(), (name, topic, selector)
                        b = locator.bounding_box()
                        assert b and b['y'] < 844 and b['y'] + b['height'] > 0, (name, selector, b)
                        b = dict(b, y=max(0,b['y']), height=min(b['height'], 60, 844-max(0,b['y'])))
                        bounds[topic].append((b, label))
                all_bounds = [b for marks in bounds.values() for b, _ in marks]
                if scope:
                    region = page.locator(scope).first.bounding_box()
                    top = max(0, region['y'] - 8)
                    bottom = min(844, region['y'] + region['height'] + 8)
                else:
                    top = max(0, min(b['y'] for b in all_bounds) - 45)
                    bottom = min(844, max(top + 320, max(b['y'] + b['height'] for b in all_bounds) + 135))
                top = min(top, max(0, bottom-320))
                top = int(top)
                height = int(bottom - top)
                raw = page.screenshot(clip=dict(x=0, y=top, width=390, height=height), animations='disabled')
                image = Image.open(io.BytesIO(raw)).convert('RGB')
                compressed = io.BytesIO()
                image.save(compressed, 'WEBP', quality=79, method=6)
                data = compressed.getvalue()
                digest = hashlib.sha256(data).hexdigest()
                filename = hashes.setdefault(digest, name + '.webp')
                (images / filename).write_bytes(data)
                for topic, marks in bounds.items():
                    annotations = []
                    for b, label in marks:
                        annotations.append(dict(label=label, x=round(b['x'], 1), y=round(b['y']-top, 1),
                                                w=round(b['width'], 1), h=round(b['height'], 1)))
                    manifest[topic] = dict(file='images/' + filename, width=390, height=height, marks=annotations)
                print(name, len(data), 'bytes', flush=True)

            reset()
            page.locator('#bsLayoutMode').select_option('split')
            click('#bsReaderTab')
            click('#bsNavigate')
            page.locator('#bsReferenceInput').fill('John 3:16')
            click('#bsDirectReference button')
            page.wait_for_function("document.querySelector('#bsBookHeading').textContent==='John'")
            page.locator('#bsVerses .bs-verse').first.wait_for()
            page.evaluate("document.querySelector('#bsBible').scrollTop=0")
            capture('bible-reader', {
                'translations': [('#bsTranslation', 'Choose English, Cebuano or Tagalog')],
                'history': [('#bsHistory', 'Open reading history'), ('#bsNavigate', 'Enter a direct reference')],
                'layouts': [('#bsLayoutMode', 'Choose Split View or fullscreen')],
                'offline': [('#bsReaderTab', 'Read the bundled Bible offline'), ('#bsBookStudyTab', 'Open offline study resources'), ('#bsNotesTab', 'Read and save local sermon notes')],
            })
            click('#bsNavigate')
            page.locator('#bsReferenceInput').fill('John 3:16')
            capture('passage-selector', {'bible-start': [('#bsBookTab', 'Choose a book and chapter'), ('#bsReferenceInput', 'Or enter a reference'), ('#bsDirectReference button', 'Tap GO')]}, '#bsNavigationDialog')
            dismiss()
            click('#bsSettings')
            capture('reading-settings', {
                'reading-display': [('#bsTheme', 'Choose paper colour'), ('#bsFontSize', 'Adjust Bible text size'), ('#bsShowMargins', 'Show Thompson topics')],
            }, '#bsSettingsDialog')
            page.locator('#mobileSignOut').scroll_into_view_if_needed()
            capture('help-and-account', {
                'account': [('#bsSettingsDialog fieldset:last-child', 'Your signed-in account'), ('#mobileSignOut', 'Sign out on this device')],
                'tutorial-replay': [('[data-open-tutorials]', 'Reopen the tutorial outline'), ('a[href="/mobile/splash"]', 'Return to the splash screen')],
            }, '#bsSettingsDialog')
            dismiss()
            # Thompson topic links are supplied by the actual chapter renderer.
            topic = page.locator('#bsVerses .bs-chain-margin button').first
            topic.click()
            page.locator('#bsChainContent .bs-scripture-ref').first.wait_for()
            capture('thompson-index', {'thompson-chain': [('#bsChainTitle', 'Thompson topic title and index'), ('#bsChainContent .bs-scripture-ref', 'Tap a connected passage'), ('#bsCloseChain', 'Return to your Bible')]}, '#bsChainDialog')
            dismiss()

            # Select real Bible words to reveal the reader's original toolbar.
            page.evaluate("""() => {
                const verse=document.querySelector('#bsVerses .bs-verse-text')||document.querySelector('#bsVerses .bs-verse');
                const range=document.createRange();range.selectNodeContents(verse);
                getSelection().removeAllRanges();getSelection().addRange(range);
                document.dispatchEvent(new Event('selectionchange'));
            }""")
            page.locator('#bsSelectionToolbar').wait_for(state='visible')
            capture('bible-selection', {
                'reader-highlighting': [('[data-selection-action="underline"]', 'Underline the selected words'), ('[data-selection-action="highlight"][data-color="#fffeb3"]', 'Choose a highlight colour')],
                'reader-copy-share': [('[data-selection-action="copy"]', 'Copy selected Scripture'), ('[data-selection-action="share"]', 'Share the selection')],
                'saved-reading': [('[data-selection-action="bookmark"]', 'Save this selected passage')],
                'study-to-notes': [('[data-selection-action="sermon-notes"]', 'Add the selection to Sermon Notes'), ('#bsNotesCurrent', 'Use your current sermon')],
            })
            dismiss()
            click('#bsWordTab')
            page.locator('#bsSearch').fill('love')
            click('#bsSearchForm button')
            page.locator('#bsWordResults .bs-loading-notice').wait_for(state='hidden')
            capture('word-study', {
                'word-study': [('#bsSearch', 'Search a word or identifier'), ('#bsSearchForm button', 'Open dictionary matches')],
                'original-languages': [('#bsSearch', 'Enter Greek, Hebrew, Strong or GK')],
                'people-related': [('#bsWordResults', 'Read dictionary results and linked entries')],
            })
            click('#bsConcordanceTab')
            page.locator('#bsConcordanceSearch').fill('love')
            click('#bsConcordanceForm button')
            page.locator('#bsConcordanceResults .bs-loading-notice').wait_for(state='hidden')
            capture('concordance', {'concordance': [('#bsConcordanceSearch', 'Search for a Bible word'), ('#bsConcordanceForm button', 'Find matching passages')]})
            click('#bsBookStudyTab')
            page.locator('#bsBookStudyResults .bs-loading-notice').wait_for(state='hidden')
            capture('book-study', {'book-study': [('#bsBookStudyTab', 'Open Book Study'), ('#bsBookStudyTitle', 'Study the current Bible book')]})
            click('#bsCommentaryTab')
            click('[data-commentary-series="exalting-jesus"]')
            page.locator('#bsCommentaryResults .bs-loading-notice').wait_for(state='hidden')
            capture('commentary', {
                'commentary': [('#bsCommentaryChoices', 'Choose a commentary series'), ('#bsCommentaryViewAll', 'Open all chapter themes')],
            })
            page.locator('#bsCommentaryResults .bs-scripture-ref').first.scroll_into_view_if_needed()
            capture('commentary-reference', {'commentary-links': [('#bsCommentaryResults .bs-scripture-ref', 'Tap a reference to preview Scripture')]})
            # A Scripture preview also exposes the real insert-into-notes action.
            click('#bsCommentaryResults .bs-scripture-ref')
            page.locator('#bsVerseText').wait_for()
            page.wait_for_function("document.querySelector('#bsVerseText').textContent.length>20")
            capture('verse-preview', {
                'verse-previews': [('#bsVerseReference', 'Preview the linked passage'), ('#bsCopyVerse', 'Copy this verse')],
                'notes-insert-scripture': [('#bsNotesInsertVerse', 'Insert Scripture into your open sermon')],
            }, '#bsVerseDialog')
            dismiss()
            click('#bsSermonTab')
            page.locator('#bsSermonResults .bs-loading-notice').wait_for(state='hidden')
            capture('sermon-outlines', {'sermon-outlines': [('#bsSermonTab', 'Open Sermon Outlines'), ('#bsSermonResults button', 'Choose an outline title')]})
            click('#bsIllustrationsTab')
            page.locator('#bsIllustrationsSuggestions .bs-loading-notice').wait_for(state='hidden')
            capture('illustrations', {'illustrations': [('#bsIllustrationsSuggestedTab', 'Suggestions for your passage'), ('#bsIllustrationsSuggestions button', 'Open an illustration')]})
            click('#bsIllustrationsBrowseTab')
            page.locator('#bsIllustrationsTopics .bs-loading-notice').wait_for(state='hidden')
            capture('illustration-topics', {'illustration-browse': [('#bsIllustrationsSearch', 'Search topics or titles'), ('#bsIllustrationsSource', 'Filter the collection'), ('#bsIllustrationsAlphabet', 'Browse topics by letter')]})

            click('#bsNotesTab')
            click('#bsNotesCreate')
            page.locator('#bsNotesMetaText').fill('John 3:16')
            page.locator('#bsNotesMetaTheme').fill('Living by the Word')
            capture('create-sermon', {'notes-create': [('#bsNotesMetaText', 'Enter the sermon Scripture'), ('#bsNotesMetaTheme', 'Enter a theme'), ('#bsNotesMetaSubmit', 'Create your sermon note')]}, '#bsNotesMetaDialog')
            click('#bsNotesMetaSubmit')
            page.locator('#bsNotesEditor').wait_for(state='visible')
            page.locator('#bsNotesEditor').press('ControlOrMeta+End')
            page.locator('#bsNotesEditor').press('Enter')
            page.locator('#bsNotesEditor').press_sequentially('Study the Word with care and put it into practice.')
            page.wait_for_function("document.querySelector('#bsNotesStatus').textContent.includes('Saved locally')")
            page.evaluate("document.querySelector('#bsNotesEditor').blur();getSelection().removeAllRanges();document.querySelector('#bsBible').scrollTop=0")
            capture('sermon-workspace', {
                'notes-metadata': [('[data-notes-edit-meta="theme"]', 'Tap the pencil to change Theme'), ('[data-notes-edit-meta="text"]', 'Change the Scripture reference')],
                'notes-read-edit': [('#bsNotesRead', 'Switch between Read and Edit')],
                'notes-save': [('#bsNotesSave', 'Save the open sermon'), ('#bsNotesStatus', 'Check the local save status')],
            })
            # Create the exact toolbar through a real DOM selection, not a mock.
            page.evaluate("""() => {
                const editor=document.querySelector('#bsNotesEditor');editor.focus();
                const range=document.createRange();range.selectNodeContents(editor.lastElementChild);
                getSelection().removeAllRanges();getSelection().addRange(range);
                document.dispatchEvent(new Event('selectionchange'));
            }""")
            page.locator('#bsNotesTools').wait_for(state='visible')
            capture('sermon-selection', {
                'notes-highlighting': [('#bsNotesEditor > :last-child', 'Select the words in your sermon'), ('[data-notes-selection-command="hiliteColor"][data-color="#fffeb3"]', 'Tap a highlight colour'), ('[data-notes-selection-command="underline"]', 'Or underline the selection')],
                'notes-copy': [('#bsNotesCopySelection', 'Copy the selected sermon text')],
            })
            capture('sermon-formatting', {
                'notes-fonts': [('#bsNotesFont', 'Choose the font family'), ('#bsNotesFontSize', 'Set size or use A+ / A-'), ('[data-notes-command="bold"]', 'Apply bold or italic')],
                'notes-structure': [('#bsNotesFormat', 'Use the visible formatting tools'), ('#bsNotesFontSize', 'Format headings and main points')],
            })
            dismiss()
            page.keyboard.press('Escape')
            click('#bsNotesActionsToggle')
            capture('sermon-options', {
                'notes-sync': [('#bsNotesActionsToggle', 'Open the sermon options'), ('#bsNotesSync', 'Sync Notes with your account')],
            })
            click('#bsNotesExport')
            page.wait_for_function("!document.querySelector('#bsNotesDownload').disabled")
            capture('sermon-export', {'notes-export': [('#bsNotesDownload', 'Download the PDF'), ('#bsNotesShare', 'Share the PDF with another app')]}, '#bsNotesExportDialog')
            dismiss()
            click('#bsNotesDelete')
            capture('sermon-delete', {'notes-delete': [('#bsNotesConfirmText', 'Read which sermon will be deleted'), ('#bsNotesConfirmCancel', 'Cancel to keep the note'), ('#bsNotesConfirmYes', 'Confirm only when you are sure')]}, '#bsNotesConfirmDialog')
            dismiss()
            click('#bsNotesAll')
            capture('sermon-library', {'notes-library': [('#bsNotesViews', 'Browse Recent, OT, NT or For Review'), ('#bsNotesSearch', 'Search your sermon library'), ('#bsNotesList button', 'Open a saved sermon')]})
            # Seed a conflict in the isolated fictional database, so the actual
            # reader renders its real conflict controls without touching Drive.
            with closing(sqlite3.connect(app.config['BIBLE_SERMON_NOTES_DATABASE'])) as db:
                db.execute("UPDATE sermon_notes SET conflict_json=? WHERE user_key=? AND deleted=0", ('{}', 'pastor:tutorial-capture'))
                db.commit()
            click('#bsNotesList button')
            page.locator('#bsNotesConflict').wait_for(state='visible')
            capture('sermon-conflict', {'sync-conflicts': [('#bsNotesKeepBoth', 'Keep both versions for review'), ('#bsNotesUseRemote', 'Replace this copy with the Drive version')]})
            with closing(sqlite3.connect(app.config['BIBLE_SERMON_NOTES_DATABASE'])) as db:
                db.execute("UPDATE sermon_notes SET conflict_json=NULL WHERE user_key=?", ('pastor:tutorial-capture',));db.commit()
            page.goto(url + '/mobile/splash')
            click('#mobilePublisher')
            # The actual optional support card is already part of the reader.
            reset()
            page.evaluate("document.querySelector('#mobileSupportDialog').showModal()")
            capture('support-card', {'publisher-support': [('#mobileSupportCopy', 'Copy the optional support account'), ('#mobileSupportContinue', 'Continue to Bible Study')]}, '#mobileSupportDialog')
            dismiss()
            app.device_state.save_profile(None)
            page.goto(url + '/')
            capture('first-sign-in', {'storage-login': [('#loginUsername', 'Sign in with your website account'), ('#loginForm button[type="submit"]', 'Log in once on this device'), ('.mobile-login-storage', 'Allow space for the offline library')]}, '.mobile-login-card')
            # Capture the actual shared app splash, with the new static artwork.
            page.goto(url + '/mobile/splash')
            capture('static-splash', {
                'startup': [('.mobile-launch-art', 'The full artwork stays still while local study tools prepare')],
                'tutorial-replay': [('#mobileTutorials', 'Open Tutorials to review any feature')],
            })
            browser.close()
        lesson_source = (output / 'tutorial.js').read_text(encoding='utf-8')
        lessons = json.JSONDecoder().raw_decode(lesson_source[lesson_source.index('['):])[0]
        assert set(manifest) == {item['id'] for item in lessons}, sorted({item['id'] for item in lessons} - set(manifest))
        (output / 'screenshots.js').write_text('"use strict";\nconst TUTORIAL_SCREENSHOTS = ' + json.dumps(manifest, separators=(',', ':')) + ';\n', encoding='utf-8')
        used = {item['file'].split('/')[-1] for item in manifest.values()}
        for old in images.glob('*.webp'):
            if old.name not in used:
                old.unlink()
        print('Completed:', len(manifest), 'topics,', len(used), 'images,', sum((images/name).stat().st_size for name in used), 'bytes')
    finally:
        server.shutdown()



def capture_store_assets(destination):
    """Export Play listing assets from real screens using fictional content."""
    import base64
    destination=Path(destination).resolve();destination.mkdir(parents=True,exist_ok=True)
    app=prepared_app(PROJECT/'.test-data/store-capture')
    app.device_state.save_profile(dict(PROFILE,user_key='pastor:store-preview',name='Study preview'))
    app.device_state.save_setting(support_last_shown=time.time())
    server=make_server('127.0.0.1',0,app,threaded=True,request_handler=QuietHandler)
    threading.Thread(target=server.serve_forever,daemon=True).start();url='http://127.0.0.1:'+str(server.server_port)
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch()
            context=browser.new_context(viewport=dict(width=360,height=640),device_scale_factor=3,is_mobile=True,has_touch=True)
            context.add_cookies([dict(name='iowo_device_gate',value='test-gate',url=url)])
            page=context.new_page();page.add_init_script('window.IOWOAndroid={tutorialActive:()=>true,copyText:()=>{},shareText:()=>{}};')
            page.goto(url+'/pastor-resources/bible-study');page.wait_for_function('window.iowoStudyReady===true',timeout=45000)
            page.locator('#bsLayoutMode').select_option('bible');page.locator('#bsReaderTab').click()
            page.locator('#bsNavigate').click();page.locator('#bsReferenceInput').fill('John 3:16');page.locator('#bsDirectReference button').click()
            page.wait_for_function("document.querySelector('#bsBookHeading').textContent==='John'")
            page.evaluate("document.querySelector('#bsBible').scrollTop=0");page.evaluate('document.fonts.ready')
            page.screenshot(path=str(destination/'01-bible-reading.png'))
            page.locator('#bsVerses .bs-chain-margin button').first.click();page.locator('#bsChainContent .bs-scripture-ref').first.wait_for()
            page.screenshot(path=str(destination/'02-thompson-chain-index.png'))
            page.locator('#bsCloseChain').click();page.locator('#bsNotesTab').click();page.locator('#bsNotesCreate').click()
            page.locator('#bsNotesMetaTheme').fill('Living by the Word');page.locator('#bsNotesMetaText').fill('2 Timothy 3:16');page.locator('#bsNotesMetaSubmit').click()
            editor=page.locator('#bsNotesEditor');editor.wait_for();editor.press('ControlOrMeta+End');editor.press('Enter');editor.press_sequentially('I. Receive the Word with faith.');editor.press('Enter');editor.press_sequentially('A. Read carefully.');editor.press('Enter');editor.press_sequentially('B. Put the Word into practice.')
            page.wait_for_function("document.querySelector('#bsNotesStatus').textContent.includes('Saved locally')")
            page.evaluate("getSelection().removeAllRanges();document.querySelector('#bsNotesEditor').blur();document.querySelector('#bsBible').scrollTop=0")
            page.screenshot(path=str(destination/'03-sermon-notes.png'))
            page.evaluate("""()=>{const e=document.querySelector('#bsNotesEditor');e.focus();const r=document.createRange();r.selectNodeContents(e.lastElementChild);getSelection().removeAllRanges();getSelection().addRange(r);document.dispatchEvent(new Event('selectionchange'));}""")
            page.locator('#bsNotesTools').wait_for(state='visible')
            page.screenshot(path=str(destination/'04-sermon-formatting.png'))
            page.keyboard.press('Escape');page.locator('#bsLayoutMode').select_option('study');page.locator('#bsCommentaryTab').click();page.locator('#bsCommentaryResults .bs-loading-notice').wait_for(state='hidden')
            page.evaluate("document.querySelector('#bsStudy').scrollTop=0")
            page.screenshot(path=str(destination/'05-study-commentary.png'))
            page.goto(url+'/mobile/tutorials/');page.wait_for_function('window.iowoTutorialReady===true');page.evaluate('document.fonts.ready')
            page.screenshot(path=str(destination/'06-tutorial-outline.png'))
            context.close()
            logo=base64.b64encode((PROJECT/'app/src/main/res/drawable-nodpi/app_icon.png').read_bytes()).decode()
            font=base64.b64encode((PROJECT/'app/src/main/assets/runtime/static/fonts/SpaceGrotesk-Variable.ttf').read_bytes()).decode()
            graphic=browser.new_page(viewport=dict(width=1024,height=500),device_scale_factor=1)
            graphic.set_content(f"""<!doctype html><html><head><style>@font-face{{font-family:UI;src:url(data:font/ttf;base64,{font})}}*{{box-sizing:border-box}}body{{margin:0;background:#f6f1e5;font-family:UI,Arial;color:#152e50}}main{{height:500px;display:flex;align-items:center;padding:50px;gap:42px;border-bottom:14px solid #c4a365}}img{{width:260px;height:350px;object-fit:contain}}h1{{font:700 58px/1.12 UI;margin:0 0 24px}}p{{font-size:26px;color:#236b70;margin:0 0 20px}}small{{font-size:18px;color:#596e7a}}</style></head><body><main><img src="data:image/png;base64,{logo}"><div><h1>IOWO D4<br>Bible Study</h1><p>Read. Study. Prepare.</p><small>Offline Bible study &amp; Sermon Notes</small></div></main></body></html>""")
            graphic.evaluate('document.fonts.ready');graphic.screenshot(path=str(destination/'feature-graphic-1024x500.png'))
            graphic.set_viewport_size(dict(width=512,height=512));graphic.set_content(f'<body style="margin:0;background:white;width:512px;height:512px;display:grid;place-items:center"><img src="data:image/png;base64,{logo}" style="width:492px;height:492px;object-fit:contain"></body>')
            graphic.screenshot(path=str(destination/'store-icon-512.png'))
            browser.close()
        for file in destination.glob('*.png'):
            with Image.open(file) as original:
                image=original.convert('RGB');image.save(file,'PNG',optimize=True)
        print('Store assets exported:',destination)
    finally:server.shutdown()


if __name__ == '__main__':
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--store-assets',type=Path)
    args=parser.parse_args()
    if args.store_assets:capture_store_assets(args.store_assets)
    else:main()

