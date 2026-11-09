"use strict";
const LESSONS = [
  {
    "id": "bible-start",
    "group": "Bible & Thompson Chain Index",
    "title": "Open a Bible passage",
    "summary": "Find a book, chapter and verse without losing your place.",
    "steps": [
      "Open the Bible tab and tap the book/chapter button above the passage.",
      "Choose Old Testament or New Testament, then a book and chapter.",
      "For a direct jump, enter a reference such as Psalm 119:105 in the navigation box and choose GO.",
      "Use the previous/next arrows above the passage or at the chapter end."
    ],
    "tip": ""
  },
  {
    "id": "thompson-chain",
    "group": "Bible & Thompson Chain Index",
    "title": "Thompson Chain Index",
    "summary": "Follow the numbered Thompson topics from a passage into its Numerical Index.",
    "steps": [
      "Open Reading Settings and enable Show Thompson margin references.",
      "In the Bible passage, tap a topic beside a verse. Expand the extra-topics control when more topics are listed.",
      "The topic window shows its Thompson index number/title, teaching sections and connected passages. Tap a Scripture reference to preview its verse.",
      "Follow a related topic or numbered index link to continue the chain. Use Back inside the topic window to return through the chain; close the window to return to the Bible."
    ],
    "tip": "Topic links are the route into the Chain Index. Concordance is a separate word-finding tool. Some topics include a chart or original source page."
  },
  {
    "id": "translations",
    "group": "Bible & Thompson Chain Index",
    "title": "Change Bible language",
    "summary": "Read the available English, Cebuano and Tagalog editions.",
    "steps": [
      "Open the Bible tab.",
      "Use the language/translation selector beside the book and chapter.",
      "Choose English - NIV, Cebuano - APSD, or Tagalog - ASND.",
      "The reader opens the same passage where the selected edition is available."
    ],
    "tip": "Study dictionaries and other reference books retain their own source language."
  },
  {
    "id": "history",
    "group": "Bible & Thompson Chain Index",
    "title": "Reading history and direct references",
    "summary": "Return to a previous passage or jump directly to a reference.",
    "steps": [
      "Tap the clock icon in the Bible navigation bar to open Reading history.",
      "Choose a saved passage to return to it.",
      "For a new location, open the book/chapter button and enter a book, chapter and verse in the direct-reference box.",
      "Close a preview window to keep your current reading position."
    ],
    "tip": ""
  },
  {
    "id": "reading-display",
    "group": "Bible & Thompson Chain Index",
    "title": "Font size, paper colour and margins",
    "summary": "Make Bible reading comfortable on your screen.",
    "steps": [
      "Use A- and A+ above the Bible passage to change reading text size.",
      "Open Reading Settings with the gear button for the font-size slider and paper colour.",
      "Choose Cream paper, White paper or Night reading.",
      "Turn Thompson margin references on or off in the same settings."
    ],
    "tip": "Bible reading size is separate from the font formatting saved inside a sermon."
  },
  {
    "id": "layouts",
    "group": "Bible & Thompson Chain Index",
    "title": "Split View and fullscreen",
    "summary": "Give the Bible or study material more space.",
    "steps": [
      "Use the layout selector to choose Split View, Bible Fullscreen or Study Fullscreen.",
      "In Split View, drag the divider to adjust the panel sizes. On a phone the panes are stacked.",
      "Keep your Bible passage in one pane while using a study tool in the other.",
      "Use the layout selector to return to Split View."
    ],
    "tip": ""
  },
  {
    "id": "reader-highlighting",
    "group": "Bible & Thompson Chain Index",
    "title": "Highlight or underline Bible text",
    "summary": "Keep personal Bible marks while reading.",
    "steps": [
      "Press and hold Bible text, then adjust the selection handles. Tapping a verse number opens actions for the whole verse.",
      "Use one of the coloured circles to highlight the selection, or U to underline it.",
      "The Bible marks belong to the signed-in reader. The same action can be used on selectable study-source text where provided.",
      "Open Reading Settings > This chapter's notes & marks to review saved chapter items."
    ],
    "tip": "Selecting text is different from tapping an individual Bible word for Word Study."
  },
  {
    "id": "reader-copy-share",
    "group": "Bible & Thompson Chain Index",
    "title": "Copy and share Scripture",
    "summary": "Include the reference when using a passage elsewhere.",
    "steps": [
      "Select Bible text or tap a verse number.",
      "Choose Copy in the selection bar to copy the Scripture and reference.",
      "Choose Share to open the available phone sharing options.",
      "Dismiss the selection bar to return to reading."
    ],
    "tip": "Copying and sharing are separate from saving a bookmark."
  },
  {
    "id": "saved-reading",
    "group": "Bible & Thompson Chain Index",
    "title": "Bookmarks and saved study selections",
    "summary": "Return to material you want to keep.",
    "steps": [
      "Select a verse or selectable study-source passage.",
      "Use Save in the selection actions to bookmark the material.",
      "Open Reading Settings for this chapter's marks, all notes/highlights, or all bookmarks.",
      "Open an item to return to its source. Use its delete control only when you want to remove that saved item."
    ],
    "tip": "An item from an unavailable edition/source may show an availability message rather than opening another text."
  },
  {
    "id": "verse-previews",
    "group": "Bible & Thompson Chain Index",
    "title": "Verse previews and footnotes",
    "summary": "Follow references while keeping the current reading location.",
    "steps": [
      "Tap a linked Scripture reference in a study tool or sermon.",
      "Read the verse in the preview window; use Copy Verse if needed.",
      "Close the window to return to the source.",
      "Expand Notes below Bible verses to read edition footnotes when present."
    ],
    "tip": ""
  },
  {
    "id": "word-study",
    "group": "Study tools",
    "title": "Word Study and dictionaries",
    "summary": "Look up words and compare the available source definitions.",
    "steps": [
      "Open Word Study and tap a word in the Bible passage.",
      "You can also enter a word, transliteration or supported identifier in Search dictionaries.",
      "Read and expand the available dictionary results. Follow linked entries or related words when offered.",
      "Use the word-type controls where provided, and return with the dictionary window's Back button."
    ],
    "tip": "Always read the surrounding Bible passage alongside dictionary definitions."
  },
  {
    "id": "original-languages",
    "group": "Study tools",
    "title": "Greek, Hebrew and identifiers",
    "summary": "Explore original-language material where it is available.",
    "steps": [
      "Look up a word in Word Study.",
      "Read the available lemma, transliteration and original-language details.",
      "Use linked Strong's, GK or dictionary identifiers when provided; the search box also accepts supported identifiers.",
      "In Pulpit commentary, tap a linked Greek term to read the source explanation and any offered Word Study link."
    ],
    "tip": "Not every passage or translation has the same linked language information."
  },
  {
    "id": "people-related",
    "group": "Study tools",
    "title": "People, related words and articles",
    "summary": "Move from a word lookup into connected study material.",
    "steps": [
      "Start with a Bible word or dictionary search.",
      "Open an offered person, related entry or article.",
      "Read the source title and its context.",
      "Use Back in the window to return through the related entries instead of losing your place."
    ],
    "tip": ""
  },
  {
    "id": "concordance",
    "group": "Study tools",
    "title": "Concordance",
    "summary": "Find printed word entries and the passages connected to them.",
    "steps": [
      "Open the Concordance tab.",
      "Select a Bible word or type a word in Search concordance and choose Search.",
      "Read the matching entries, excerpts and references.",
      "Tap a linked verse to preview it, or a linked Thompson topic to explore that topic."
    ],
    "tip": "Concordance searches words; the Thompson Chain Index follows topics. They complement each other."
  },
  {
    "id": "book-study",
    "group": "Study tools",
    "title": "Book Study",
    "summary": "Read the introduction and outline for a Bible book.",
    "steps": [
      "Choose the Bible book you want to study in the reader.",
      "Open the Book Study tab beside Bible.",
      "Read its introduction and available outline sections.",
      "Return to Bible to read a chapter, or choose another book for a different introduction."
    ],
    "tip": ""
  },
  {
    "id": "commentary",
    "group": "Study tools",
    "title": "Commentary series and chapter themes",
    "summary": "Compare explanations without changing the Bible passage.",
    "steps": [
      "Open Commentary and choose an available series: Wiersbe, Exalting Jesus, Moody or Pulpit.",
      "For a series with chapter themes, choose a theme or use View all to see the complete list.",
      "Use Previous and Next to move between commentary sections.",
      "For Pulpit, choose a commentary section when offered. Linked Bible references open verse previews."
    ],
    "tip": "Some series explain a whole chapter; others divide it into themes. An unavailable match is not an app error."
  },
  {
    "id": "commentary-links",
    "group": "Study tools",
    "title": "Commentary references and source selections",
    "summary": "Use supporting references and keep helpful material.",
    "steps": [
      "Tap a linked Bible reference in the commentary to preview it.",
      "Open linked dictionary or Greek explanations where offered.",
      "Select source text to use its Copy, highlight, Save or Add to Sermon Notes actions.",
      "Close the preview or use Back to return to the commentary."
    ],
    "tip": ""
  },
  {
    "id": "sermon-outlines",
    "group": "Study tools",
    "title": "Sermon Outlines",
    "summary": "Use an existing outline as a study and preparation resource.",
    "steps": [
      "Choose the relevant Bible chapter.",
      "Open Sermon Outlines and select a title.",
      "Read the original outline and its source details; linked Scripture references open previews.",
      "Select useful text to copy it or add it to Sermon Notes. Return to the title list to choose another outline."
    ],
    "tip": ""
  },
  {
    "id": "illustrations",
    "group": "Study tools",
    "title": "Suggested sermon illustrations",
    "summary": "Find illustrations connected to the current passage.",
    "steps": [
      "Open Sermon Illustrations.",
      "Use Suggested for the current chapter or selected verse range.",
      "Open an illustration to read its full text and source credit.",
      "Use Copy Illustration or select text to add it to your sermon notes."
    ],
    "tip": "Keep the source credit when reusing an illustration."
  },
  {
    "id": "illustration-browse",
    "group": "Study tools",
    "title": "Browse illustrations by topic",
    "summary": "Look beyond the current-passage suggestions.",
    "steps": [
      "In Sermon Illustrations, open Browse by Topic.",
      "Choose an alphabet letter, search text, or a topic to narrow the list.",
      "Use the source/filter choices where available and load more results when offered.",
      "Open an illustration, then return to the list to continue browsing."
    ],
    "tip": ""
  },
  {
    "id": "study-to-notes",
    "group": "Study tools",
    "title": "Add study material to Sermon Notes",
    "summary": "Bring Scripture or study-source text into a sermon.",
    "steps": [
      "Select the Bible or study-source text you want.",
      "Choose Add to Sermon Notes in the selection toolbar.",
      "Choose an existing sermon or create a new one with Text and Theme.",
      "To send selections directly to the currently open sermon, enable Current notes beside the action."
    ],
    "tip": "Check the destination sermon before adding text. Use Undo in the editor if an insertion needs to be removed."
  },
  {
    "id": "notes-create",
    "group": "Sermon Notes",
    "title": "Create a sermon note",
    "summary": "Start a sermon with its Bible reference and theme.",
    "steps": [
      "Open Sermon Notes, then Create Notes.",
      "Enter Text (the Bible reference) and Theme (the sermon title). Both are required.",
      "Choose Create Notes to open the editor.",
      "Write below the headings. The editor recognises common main-point and subpoint markers as you type."
    ],
    "tip": "Enter your own Theme and Text when creating a sermon. These screenshots show a sample note."
  },
  {
    "id": "notes-library",
    "group": "Sermon Notes",
    "title": "All Notes, search and book filters",
    "summary": "Find an existing sermon quickly.",
    "steps": [
      "Open Sermon Notes > All Notes.",
      "Use Recent, OT, NT or For Review. OT/NT lets you choose a Bible book.",
      "Use Search for words in the theme, Bible text/reference or sermon body. Clear the search or book filter to see more results.",
      "Tap a sermon to open it. Local/sync/conflict labels describe its backup state."
    ],
    "tip": ""
  },
  {
    "id": "notes-metadata",
    "group": "Sermon Notes",
    "title": "Edit Theme and Text",
    "summary": "Correct the sermon title or Bible reference.",
    "steps": [
      "Open the sermon.",
      "Tap the pencil beside Theme or Text/reference above the editor.",
      "Edit the values in the existing form and save.",
      "Confirm the updated headings before continuing to write."
    ],
    "tip": ""
  },
  {
    "id": "notes-read-edit",
    "group": "Sermon Notes",
    "title": "Read Notes and Edit Notes",
    "summary": "Switch between reading and writing.",
    "steps": [
      "Open the sermon in Sermon Notes.",
      "Choose Read Notes in the normal top action bar to view the formatted reading preview.",
      "Tap linked Scripture references to open verse previews.",
      "Choose Edit Notes to return to the editable sermon."
    ],
    "tip": "When text is selected, the selection toolbar temporarily replaces the normal top actions. Dismiss it to see Read/Save/Delete again."
  },
  {
    "id": "notes-highlighting",
    "group": "Sermon Notes",
    "title": "Highlight in Sermon Notes",
    "summary": "Colour selected words without changing your Bible highlights.",
    "steps": [
      "Open a sermon in Edit Notes mode. Press and hold the text you want, then adjust the selection handles.",
      "The top action bar switches to Copy, U and the highlight colours. Tap a colour to highlight the selected words.",
      "Use U to underline the selection. Copy copies the selected sermon text.",
      "Tap outside, dismiss the bar with X, or end the selection to restore Create/All Notes/Read/Save/Delete."
    ],
    "tip": "These are rich-text changes inside this sermon. They are separate from Bible-reader marks."
  },
  {
    "id": "notes-fonts",
    "group": "Sermon Notes",
    "title": "Font, size, bold, italic and colour",
    "summary": "Use More formatting on the selected sermon text.",
    "steps": [
      "Select text in the sermon editor and open More formatting.",
      "Choose a font family in the shortened dropdown. Font size, A+ and A- sit beside it.",
      "Use the next row for case, Bold, Italic, text colour, Clear and Undo.",
      "Review the result and use Save or let autosave finish."
    ],
    "tip": "Clear removes formatting from the selection; Undo reverses the most recent supported edit."
  },
  {
    "id": "notes-structure",
    "group": "Sermon Notes",
    "title": "Main points, subpoints and headings",
    "summary": "Keep a sermon readable as you write.",
    "steps": [
      "Enter a main point with a Roman numeral marker, such as I. or II. followed by its text.",
      "Use lettered markers such as A. or B. for subpoints.",
      "Use paragraphs to keep Scripture, explanations and applications separate.",
      "Select text and use More formatting to adjust emphasis or size where needed."
    ],
    "tip": ""
  },
  {
    "id": "notes-insert-scripture",
    "group": "Sermon Notes",
    "title": "Preview and insert Scripture into a sermon",
    "summary": "Read recognised references and add the passage text.",
    "steps": [
      "Write a recognised Bible reference in the sermon, such as John 3:16.",
      "Tap the reference to open its verse preview.",
      "Choose Insert verse into sermon notes in the preview. An editor-origin preview inserts after its reference.",
      "For previews opened elsewhere, choose the destination note when asked. Review the insertion and use Undo if needed."
    ],
    "tip": ""
  },
  {
    "id": "notes-copy",
    "group": "Sermon Notes",
    "title": "Copy selected sermon text",
    "summary": "Reuse an excerpt without exporting the whole sermon.",
    "steps": [
      "Select text inside Edit Notes.",
      "Tap Copy in the top selection toolbar.",
      "Paste the text into the destination app or another location.",
      "For a complete formatted document, use Export Notes instead."
    ],
    "tip": ""
  },
  {
    "id": "notes-save",
    "group": "Sermon Notes",
    "title": "Autosave and manual Save",
    "summary": "Keep sermon edits on the device, including offline.",
    "steps": [
      "Write or format a sermon in Edit Notes.",
      "Watch the status line change from saving to saved locally.",
      "Dismiss the selection toolbar when needed, then use Save in the normal top actions to save manually.",
      "Use Sync Notes separately to back up or restore through the online connection."
    ],
    "tip": "Saved locally does not mean the latest edit has reached online backup."
  },
  {
    "id": "notes-export",
    "group": "Sermon Notes",
    "title": "Export, download and share a PDF",
    "summary": "Make a document from the current sermon.",
    "steps": [
      "Open the sermon and finish saving your edits.",
      "Open the Sermon Notes options gear and choose Export Notes.",
      "Wait for the PDF preview/actions to become available.",
      "Choose Download to select a file location, or Share to send it using an available phone app."
    ],
    "tip": "Export is separate from Sync Notes. A saved PDF is not a two-way editable-notes backup."
  },
  {
    "id": "notes-delete",
    "group": "Sermon Notes",
    "title": "Delete a sermon safely",
    "summary": "Understand local deletion and backup propagation.",
    "steps": [
      "Open the sermon you intend to remove.",
      "Dismiss the selection toolbar and choose Delete in the normal actions.",
      "Read the confirmation, including the sermon title. Cancel if it is not the intended sermon.",
      "Only confirm when you want it deleted. A later Sync Notes also propagates the deletion to the backup connection."
    ],
    "tip": "Do not use Delete as a way to refresh a list. Keep an export/backup of important sermons."
  },
  {
    "id": "notes-sync",
    "group": "Saving, sync & offline use",
    "title": "Sync Notes and restore a library",
    "summary": "Back up local notes and retrieve the connected online library.",
    "steps": [
      "Connect to the internet and sign in to the correct account.",
      "In Sermon Notes, open the options gear and choose Sync Notes.",
      "Let the progress run. Sync can back up local changes, restore notes and apply confirmed remote deletions.",
      "Review the final status and the All Notes list. You can continue using notes saved on the device when offline."
    ],
    "tip": "The first restore can take longer for a large library. Starting the app prepares local notes; it does not silently start a Drive sync."
  },
  {
    "id": "sync-conflicts",
    "group": "Saving, sync & offline use",
    "title": "Resolve a sync conflict",
    "summary": "Keep deliberate control over two changed versions.",
    "steps": [
      "Open the sermon marked with a conflict.",
      "Read the message and review which version you need.",
      "Keep both preserves a separate copy for comparison. Use Drive version chooses the remote version and asks for confirmation.",
      "Finish reviewing the result, then sync again when appropriate."
    ],
    "tip": "Do not choose the remote version merely to clear a warning if it would discard edits you still need."
  },
  {
    "id": "offline",
    "group": "Saving, sync & offline use",
    "title": "What works offline",
    "summary": "Know which actions need an internet connection.",
    "steps": [
      "Complete first login and offline-library setup while connected.",
      "Bible reading, installed study resources and saved sermon notes can then be used offline.",
      "Local editing and Save keep work on the device.",
      "First login, online backup/restore and online sharing destinations require an internet connection."
    ],
    "tip": "Do not uninstall or clear app data to fix a temporary connection problem; that can remove local notes."
  },
  {
    "id": "startup",
    "group": "Saving, sync & offline use",
    "title": "Startup progress and study verses",
    "summary": "Understand what the loading screen prepares.",
    "steps": [
      "Open the app and watch the startup progress.",
      "Thirty study-focused Bible verses can rotate while the local workspace prepares.",
      "The Bible passage, local sermon-note list and current-chapter tools prepare before the reader opens.",
      "If startup cannot finish, use Retry. Existing notes are kept."
    ],
    "tip": "This preparation uses installed/local resources; it is different from restoring notes with Sync Notes."
  },
  {
    "id": "storage-login",
    "group": "Saving, sync & offline use",
    "title": "First login and library preparation",
    "summary": "Set up the app once for offline use.",
    "steps": [
      "Read and accept the initial use/privacy agreement.",
      "Sign in online with your existing website account. The app remembers the authorised device session.",
      "Review available storage and prepare the bundled study library.",
      "Wait for setup to finish. Later launches reuse the prepared library and saved account."
    ],
    "tip": "Allow enough device storage. Interrupted setup can resume; avoid removing existing private files manually."
  },
  {
    "id": "account",
    "group": "Saving, sync & offline use",
    "title": "Account and sign out",
    "summary": "Keep personal reading and sermons tied to the correct account.",
    "steps": [
      "Open Reading Settings to see the current account.",
      "Use Sign out on this device only when you intend to leave that account.",
      "Sign in online again to reconnect or use another authorised account.",
      "Return to the correct account to see its private notes and saved reading."
    ],
    "tip": "Signing out keeps protected local notes; clearing app data or uninstalling is a different action."
  },
  {
    "id": "tutorial-replay",
    "group": "App help & additional functions",
    "title": "Replay a tutorial or review one topic",
    "summary": "Find the exact help you need later.",
    "steps": [
      "Open Tutorials on the splash screen, or Tutorials & help in Reading Settings.",
      "Choose a group in the outline, such as Sermon Notes.",
      "Choose the exact topic, such as Highlight in Sermon Notes, or use the tutorial search.",
      "Start the guided tour to replay the main steps, or return to the app when finished."
    ],
    "tip": "Screenshots show the real app with sample content. Viewing them does not change your notes or Bible marks."
  },
  {
    "id": "publisher-support",
    "group": "App help & additional functions",
    "title": "About Publisher and the support card",
    "summary": "Read about the project or continue past optional support.",
    "steps": [
      "Use About Publisher on the splash screen to read the project background.",
      "The support card can appear after startup at most once every three days.",
      "Copy GCash Number copies the displayed account; Continue or Back dismisses the card.",
      "App access remains available without a donation."
    ],
    "tip": "Tutorials take priority while they are open. Support does not interrupt an active editing session."
  }
];

(() => {
const $ = id => document.getElementById(id);
const GUIDE = ['bible-start','thompson-chain','word-study','commentary','reader-highlighting','notes-create','notes-highlighting','notes-sync'];
const PROGRESS = 'iowo-tutorial-progress-v1';
let reviewed = new Set(), current = null, touring = false;
try { reviewed = new Set(JSON.parse(localStorage.getItem(PROGRESS) || '[]')); } catch (_) {}
const save = () => { try { localStorage.setItem(PROGRESS, JSON.stringify([...reviewed])); } catch (_) {} };
const button = (text, action, parent, cls='') => {
    const node=document.createElement('button');node.type='button';node.textContent=text;node.className=cls;node.addEventListener('click',action);parent.append(node);return node;
};
function outline() {
    const query=$('tutorialSearch').value.toLowerCase().trim(), groups=new Map();
    LESSONS.forEach(lesson=>{
        if(query && ![lesson.title,lesson.group,lesson.summary,...lesson.steps].join(' ').toLowerCase().includes(query))return;
        if(!groups.has(lesson.group))groups.set(lesson.group,[]);groups.get(lesson.group).push(lesson);
    });
    $('tutorialOutline').replaceChildren();
    groups.forEach((lessons,name)=>{
        const section=document.createElement('details');section.open=Boolean(query)||!current||lessons.some(l=>l.id===current.id);
        const heading=document.createElement('summary');heading.textContent=name;
        const count=document.createElement('small');count.textContent=lessons.length;heading.append(count);section.append(heading);
        lessons.forEach(lesson=>{
            const node=button(lesson.title,()=>openLesson(lesson.id,false),section);
            node.dataset.lesson=lesson.id;node.dataset.reviewed=String(reviewed.has(lesson.id));
            node.setAttribute('aria-current',String(current?.id===lesson.id));
            if(reviewed.has(lesson.id))node.setAttribute('aria-label',lesson.title+', reviewed');
        });$('tutorialOutline').append(section);
    });$('noResults').hidden=groups.size>0;
}
function showOutline() {
    current=null;touring=false;document.body.classList.remove('has-lesson');$('lessonPanel').hidden=true;
    history.replaceState(null,'','#outline');outline();$('outlineTitle').focus({preventScroll:true});window.scrollTo(0,0);
}
function finish() {
    if(window.IOWOTutorial?.finish){window.IOWOTutorial.finish();return;}
    location.href='/';
}
function openLesson(id,tour=false) {
    const lesson=LESSONS.find(item=>item.id===id);if(!lesson)return;
    current=lesson;touring=tour;document.body.classList.add('has-lesson');$('lessonPanel').hidden=false;
    $('lessonCategory').textContent=lesson.group;$('lessonTitle').textContent=lesson.title;$('lessonSummary').textContent=lesson.summary;
    $('lessonSteps').replaceChildren(...lesson.steps.map(text=>{const li=document.createElement('li');li.textContent=text;return li;}));
    $('lessonTip').hidden=!lesson.tip;$('lessonTip').textContent=lesson.tip;
    const position=GUIDE.indexOf(id);$('tourPosition').hidden=!tour;$('tourProgress').hidden=!tour;$('skipTour').hidden=!tour;
    $('tourPosition').textContent=`${position+1} of ${GUIDE.length}`;$('tourProgress').value=position+1;
    const index=tour?position:LESSONS.indexOf(lesson), length=tour?GUIDE.length:LESSONS.length;
    $('previousLesson').disabled=index===0;$('nextLesson').textContent=index===length-1?(tour?'Finish tour':'All tutorials'):'Next';
    $('markReviewed').textContent=reviewed.has(id)?'Reviewed':'Mark reviewed';
    history.replaceState(null,'','#'+id);outline();showScreenshot(lesson);
    $('lessonTitle').focus({preventScroll:true});window.scrollTo(0,0);
}
function advance(delta) {
    if(!current)return;
    const ids=touring?GUIDE:LESSONS.map(l=>l.id), index=ids.indexOf(current.id);
    if(delta>0){reviewed.add(current.id);save();}
    if(index+delta>=ids.length){if(touring)finish();else showOutline();return;}
    if(index+delta>=0)openLesson(ids[index+delta],touring);
}
const SVG_NS='http://www.w3.org/2000/svg';
function svgNode(tag,attributes,parent) {
    const node=document.createElementNS(SVG_NS,tag);
    for(const [name,value] of Object.entries(attributes))node.setAttribute(name,String(value));
    parent.append(node);return node;
}
function createScreenshot(screen,title) {
    const canvas=document.createElement('span');canvas.className='annotated-screen';
    canvas.style.aspectRatio=`${screen.width} / ${screen.height}`;
    const image=document.createElement('img');image.src=screen.file;image.alt=`${title}: screenshot of the app with sample content`;
    image.width=screen.width;image.height=screen.height;image.decoding='async';image.draggable=false;
    canvas.append(image);
    const overlay=svgNode('svg',{viewBox:`0 0 ${screen.width} ${screen.height}`,'aria-hidden':'true',focusable:'false',class:'screenshot-arrows'},canvas);
    const positions=[];
    screen.marks.forEach((mark,index)=>{
        const targetX=Math.max(8,Math.min(screen.width-8,mark.x+mark.w/2));
        const targetY=Math.max(8,Math.min(screen.height-8,mark.y+mark.h/2));
        let badgeX=Math.max(22,Math.min(screen.width-22,mark.badge?.x ?? targetX+(targetX<screen.width/2?76:-76)));
        let badgeY=Math.max(23,Math.min(screen.height-23,mark.badge?.y ?? targetY+(targetY<70?65:-54)));
        // Keep numbered badges apart when neighbouring controls share a row.
        for(let attempt=0;attempt<8&&positions.some(p=>Math.hypot(p.x-badgeX,p.y-badgeY)<39);attempt++) {
            badgeY=Math.max(23,Math.min(screen.height-23,badgeY+(attempt%2?70:-40)));
            badgeX=Math.max(22,Math.min(screen.width-22,badgeX+(attempt%2?-48:48)));
        }
        positions.push({x:badgeX,y:badgeY});
        const dx=targetX-badgeX,dy=targetY-badgeY,length=Math.hypot(dx,dy)||1,ux=dx/length,uy=dy/length;
        const startX=badgeX+ux*15,startY=badgeY+uy*15,endX=targetX-ux*8,endY=targetY-uy*8;
        for(const [stroke,width] of [['#fffdf7',6],['#b94318',2.5]])
            svgNode('path',{d:`M${startX},${startY} L${endX},${endY}`,fill:'none',stroke,'stroke-width':width,'stroke-linecap':'round'},overlay);
        svgNode('polygon',{points:`${targetX},${targetY} ${targetX-ux*12+uy*5},${targetY-uy*12-ux*5} ${targetX-ux*12-uy*5},${targetY-uy*12+ux*5}`,fill:'#b94318',stroke:'#fffdf7','stroke-width':1},overlay);
        svgNode('circle',{cx:badgeX,cy:badgeY,r:15,fill:'#153858',stroke:'#fffdf7','stroke-width':2},overlay);
        const number=svgNode('text',{x:badgeX,y:badgeY+4,'text-anchor':'middle',fill:'white','font-size':12,'font-weight':700,'font-family':'TutorialUI,Arial,sans-serif'},overlay);number.textContent=index+1;
    });
    image.onerror=()=>{$('screenshotError').hidden=false;};
    return canvas;
}
function showScreenshot(lesson) {
    const screen=TUTORIAL_SCREENSHOTS[lesson.id];
    $('screenshotCanvas').replaceChildren();$('screenshotLabels').replaceChildren();$('screenshotError').hidden=true;
    $('lessonScreenshot').hidden=!screen;
    if(!screen)return;
    $('screenshotCanvas').append(createScreenshot(screen,lesson.title));
    $('screenshotLabels').replaceChildren(...screen.marks.map(mark=>{const li=document.createElement('li');li.textContent=mark.label;return li;}));
    $('enlargeScreenshot').setAttribute('aria-label','Enlarge screenshot: '+lesson.title);
}
$('enlargeScreenshot').onclick=()=>{
    if(!current)return;const screen=TUTORIAL_SCREENSHOTS[current.id];if(!screen)return;
    $('zoomTitle').textContent=current.title;$('zoomCanvas').replaceChildren(createScreenshot(screen,current.title));
    $('zoomLabels').replaceChildren(...[...$('screenshotLabels').children].map(node=>node.cloneNode(true)));
    $('screenshotZoom').classList.remove('is-zoomed');$('zoomToggle').textContent='Zoom in';$('zoomToggle').setAttribute('aria-pressed','false');
    $('screenshotZoom').showModal();$('zoomScroll').scrollTo(0,0);
};
$('zoomToggle').onclick=()=>{
    const zoomed=$('screenshotZoom').classList.toggle('is-zoomed');
    $('zoomToggle').textContent=zoomed?'Fit screen':'Zoom in';$('zoomToggle').setAttribute('aria-pressed',String(zoomed));
};
$('closeZoom').onclick=()=>$('screenshotZoom').close();
$('screenshotZoom').addEventListener('close',()=>{$('zoomCanvas').replaceChildren();$('enlargeScreenshot').focus({preventScroll:true});});
$('tutorialSearch').addEventListener('input',outline);
$('startTour').onclick=()=>openLesson(GUIDE[0],true);
$('outlineHome').onclick=event=>{event.preventDefault();showOutline();};$('backToOutline').onclick=showOutline;
$('closeTutorials').onclick=finish;$('skipTour').onclick=finish;
$('previousLesson').onclick=()=>advance(-1);$('nextLesson').onclick=()=>advance(1);
$('markReviewed').onclick=()=>{if(!current)return;reviewed.add(current.id);save();$('markReviewed').textContent='Reviewed';outline();};
[['thompson-chain','Thompson Index'],['notes-highlighting','Highlight in Sermon Notes'],['notes-sync','Save & sync']].forEach(([id,title])=>button(title,()=>openLesson(id,false),$('quickLinks')));
window.iowoTutorialBack=()=>{if($('screenshotZoom').open){$('screenshotZoom').close();return true;}if(!current)return false;if(touring&&GUIDE.indexOf(current.id)>0)advance(-1);else showOutline();return true;};
window.addEventListener('hashchange',()=>{
    const id=location.hash.slice(1);
    if(id==='outline')showOutline();else if(LESSONS.some(lesson=>lesson.id===id))openLesson(id,false);
});
const query=new URLSearchParams(location.search), hash=location.hash.slice(1);
if(query.get('tour')==='1')openLesson(GUIDE[0],true);else if(LESSONS.some(l=>l.id===hash))openLesson(hash);else outline();
window.iowoTutorialReady=true;
})();
