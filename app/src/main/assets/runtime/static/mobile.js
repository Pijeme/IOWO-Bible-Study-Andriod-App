(() => {
    'use strict';
    const config=JSON.parse(document.getElementById('mobileConfig').textContent);
    const $=id=>document.getElementById(id);
    const status=(message,error=false)=>{if($('mobileStatus')){$('mobileStatus').textContent=message;$('mobileStatus').dataset.error=String(error)}};
    const bytes=value=>(value/1e9).toFixed(2)+' GB';
    async function call(url,data,method='POST'){
        const options=data===undefined?{}:{method,headers:{'Content-Type':'application/json','X-CSRF-Token':config.csrf},body:JSON.stringify(data)};
        const response=await fetch(url,{credentials:'same-origin',cache:'no-store',...options});
        const result=await response.json();
        if(!response.ok||!result.ok)throw Error(result.error||'The request could not be completed.');
        return result;
    }
    if($('mobilePublisher')){
        let opening=setTimeout(()=>location.replace('/'),3000);
        $('mobilePublisher').addEventListener('click',()=>clearTimeout(opening));
        $('mobileTutorials')?.addEventListener('click',()=>clearTimeout(opening));
        window.addEventListener('pagehide',()=>clearTimeout(opening));
        window.addEventListener('pageshow',event=>{if(event.persisted){clearTimeout(opening);opening=setTimeout(()=>location.replace('/'),3000)}});
    }
    document.querySelectorAll('[data-open-tutorials]').forEach(link=>link.addEventListener('click',event=>{
        if(!window.IOWOAndroid?.openTutorials)return;
        event.preventDefault();window.IOWOAndroid.openTutorials();
    }));
    $('mobileSignOut')?.addEventListener('click',async()=>{if(!confirm('Sign out on this device? Your saved local notes will stay protected under your account.'))return;try{await call('/mobile/logout',{});location.href='/'}catch(error){alert(error.message)}});
    $('agreementForm')?.addEventListener('submit',async event=>{event.preventDefault();try{await call('/mobile/agree',{accepted:$('agreementAccepted').checked});location.replace('/')}catch(error){status(error.message,true)}});
    $('loginForm')?.addEventListener('submit',async event=>{
        event.preventDefault();const button=event.target.querySelector('button[type=submit]');button.disabled=true;status('Confirming your website account…');
        try{await call('/mobile/login',{username:$('loginUsername').value,password:$('loginPassword').value,website:config.website});$('loginPassword').value='';location.replace('/')}
        catch(error){status(error.message,true)}finally{button.disabled=false}
    });
    $('mobileTogglePassword')?.addEventListener('click',()=>{
        const showing=$('loginPassword').type==='password';$('loginPassword').type=showing?'text':'password';
        $('mobileTogglePassword').setAttribute('aria-label',showing?'Hide password':'Show password');
        $('mobileTogglePassword').setAttribute('aria-pressed',String(showing));
        $('mobilePasswordSlash').toggleAttribute('hidden',!showing);
    });
    async function pollSetup(){
        try{const data=await call('/mobile/setup/status');$('setupMessage').textContent=data.error||data.message||'Preparing library…';
            if(data.ready){location.replace('/');return}
            $('setupBar').value=data.total?data.completed/data.total*100:0;
            if(data.running)setTimeout(pollSetup,700);else{$('prepareLibrary').disabled=false;if(data.error)status(data.error,true)}
        }catch(error){status(error.message,true);$('prepareLibrary').disabled=false}
    }
    if($('prepareLibrary')){
        call('/mobile/storage').then(data=>{$('storageCheck').textContent=bytes(data.free_bytes)+' available · '+bytes(data.required_bytes)+' needed for setup.';$('prepareLibrary').disabled=!data.sufficient;if(!data.sufficient)status('Free some storage, then reopen this screen.',true)}).catch(error=>status(error.message,true));
        $('prepareLibrary').addEventListener('click',async()=>{$('prepareLibrary').disabled=true;$('setupProgress').hidden=false;try{await call('/mobile/setup',{});pollSetup()}catch(error){status(error.message,true);$('prepareLibrary').disabled=false}});
        pollSetup();
    }
    document.querySelectorAll('.mobile-delete-mark').forEach(button=>button.addEventListener('click',async()=>{
        const card=button.closest('[data-item]');if(!confirm('Remove this saved item from your account on this device?'))return;
        const url=card.dataset.kind==='study'?'/pastor-resources/bible-study/api/study-saves/'+card.dataset.item:'/pastor-resources/bible-study/api/personal/'+card.dataset.kind+'/'+card.dataset.item;
        try{await call(url,{},'DELETE');card.remove()}catch(error){alert(error.message)}
    }));
    // The support card is optional and never interrupts an editing session.
    // Persist the 72-hour cadence in app-private settings, across app updates.
    const support=$('mobileSupportDialog');
    let supportChecking=false,supportNextCheck=0;
    async function showSupportReminder(){
        if(!support || supportChecking || Date.now()<supportNextCheck || document.visibilityState==='hidden' || !window.iowoStudyReady)return;
        if(window.IOWOAndroid?.tutorialActive?.())return;
        if(document.querySelector('dialog[open]') || document.activeElement?.matches('input,textarea,[contenteditable=true]'))return;
        supportChecking=true;
        try{
            const result=await call('/mobile/support/claim',{});
            supportNextCheck=result.next_at*1000;
            if(result.show)support.showModal();
        }catch(_error){supportNextCheck=Date.now()+60000;/* Optional support never prevents access. */}
        finally{supportChecking=false;}
    }
    $('mobileSupportContinue')?.addEventListener('click',()=>support.close());
    $('mobileSupportCopy')?.addEventListener('click',async()=>{
        const button=$('mobileSupportCopy');let copied=false;
        try{await navigator.clipboard.writeText(support.dataset.gcash);copied=true;}
        catch(_error){
            const text=document.createElement('textarea');text.value=support.dataset.gcash;support.append(text);text.select();
            try{copied=document.execCommand('copy');}catch(_){}text.remove();
        }
        button.textContent=copied?'Number copied':'Select the number above to copy';
        setTimeout(()=>{button.textContent='Copy GCash Number';},1700);
    });
    window.addEventListener('iowo-study-ready',showSupportReminder);
    window.addEventListener('iowo-tutorial-closed',showSupportReminder);
    document.addEventListener('visibilitychange',showSupportReminder);
    if(window.iowoStudyReady)showSupportReminder();

    // WebView does not implement Chrome's file share/download UI for blob URLs.
    // The native bridge writes only explicitly requested PDF/JSON exports.
    async function exportFile(file,share){
        const buffer=new Uint8Array(await file.arrayBuffer());let binary='';
        for(let i=0;i<buffer.length;i+=8192)binary+=String.fromCharCode(...buffer.subarray(i,i+8192));
        window.IOWOAndroid.exportFile(btoa(binary),file.name,file.type,Boolean(share));
    }
    window.iowoExportFile=exportFile;
    if(window.IOWOAndroid){
        try{Object.defineProperty(navigator,'share',{configurable:true,value:async data=>{if(data.files?.length){await exportFile(data.files[0],true);return}window.IOWOAndroid.shareText(data.text||data.title||'')}});Object.defineProperty(navigator,'canShare',{configurable:true,value:data=>!data.files||data.files.length===1})}catch(_){}
        try{Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>window.IOWOAndroid.copyText(String(text))}})}catch(_){}
    }
    window.iowoHandleBack=()=>{
        if(document.querySelector('#bsNotesTools[data-open="true"]:not([hidden])')){
            $('bsNotesDismissSelection').click();return true;
        }
        const dialog=[...document.querySelectorAll('dialog[open]')].at(-1);if(dialog){dialog.close();return true}
        if(document.querySelector('[aria-expanded=true][id^=bsNotes]')){document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',bubbles:true}));return true}
        return false;
    };
})();
