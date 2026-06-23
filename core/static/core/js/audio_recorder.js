(function(){
  const attachToggle=document.getElementById('attachToggle');
  const attachMenu=document.getElementById('attachMenu');
  const tipoEnvio=document.getElementById('tipoEnvio');
  const selectedFile=document.getElementById('selectedFile');
  const messageText=document.getElementById('messageText');

  if(attachToggle&&attachMenu){
    attachToggle.addEventListener('click',()=>attachMenu.classList.toggle('d-none'));
    attachMenu.querySelectorAll('button[data-target]').forEach(btn=>{
      btn.addEventListener('click',()=>{
        const input=document.getElementById(btn.dataset.target);
        if(input){ input.click(); }
        attachMenu.classList.add('d-none');
      });
    });
  }

  ['docInput','mediaInput','audioFileInput'].forEach(id=>{
    const input=document.getElementById(id);
    if(!input)return;
    input.addEventListener('change',()=>{
      if(input.files&&input.files[0]){
        if(tipoEnvio) tipoEnvio.value=input.dataset.tipo||'DOCUMENTO';
        if(selectedFile){ selectedFile.textContent='Anexo: '+input.files[0].name; selectedFile.classList.remove('d-none'); }
      }
    });
  });

  if(messageText){
    messageText.addEventListener('input',()=>{
      messageText.style.height='auto';
      messageText.style.height=Math.min(messageText.scrollHeight,120)+'px';
    });

    // Envia com Enter, mantendo Shift+Enter para quebra de linha.
    messageText.addEventListener('keydown',(e)=>{
      if(e.key === 'Enter' && !e.shiftKey && !e.isComposing){
        e.preventDefault();
        const form=document.getElementById('sendForm');
        if(form){
          if(typeof form.requestSubmit === 'function') form.requestSubmit();
          else form.submit();
        }
      }
    });
  }

  const startBtn=document.getElementById('startRecord');
  const stopBtn=document.getElementById('stopRecord');
  const cancelBtn=document.getElementById('cancelRecord');
  const discardBtn=document.getElementById('discardAudio');
  const statusEl=document.getElementById('recordingStatus');
  const preview=document.getElementById('audioPreview');
  const previewBox=document.getElementById('audioPreviewBox');
  const input=document.getElementById('audioBlobInput');
  const recordBar=document.getElementById('recordBar');
  const composer=document.getElementById('sendForm');
  if(!startBtn||!stopBtn||!preview||!input||!recordBar)return;

  let recorder, chunks=[], stream, timer, startedAt, previewUrl=null;
  function setStatus(txt){ if(statusEl) statusEl.textContent=txt; }
  function startTimer(){
    startedAt=Date.now();
    timer=setInterval(()=>{
      const s=Math.floor((Date.now()-startedAt)/1000);
      const mm=String(Math.floor(s/60)).padStart(2,'0');
      const ss=String(s%60).padStart(2,'0');
      setStatus('🔴 Gravando... '+mm+':'+ss);
    },300);
  }
  function cleanupStream(){ if(stream){ stream.getTracks().forEach(t=>t.stop()); stream=null; } clearInterval(timer); }
  function resetRecording(){
    cleanupStream(); chunks=[];
    if(previewUrl){ URL.revokeObjectURL(previewUrl); previewUrl=null; }
    if(input) input.value='';
    if(preview) preview.removeAttribute('src');
    if(previewBox) previewBox.classList.add('d-none');
    recordBar.classList.add('d-none');
    if(composer) composer.classList.remove('d-none');
  }

  startBtn.addEventListener('click', async ()=>{
    try{
      stream=await navigator.mediaDevices.getUserMedia({audio:true});
      chunks=[]; recorder=new MediaRecorder(stream);
      recorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data); };
      recorder.onstop=()=>{
        cleanupStream();
        const blob=new Blob(chunks,{type:'audio/webm'});
        const file=new File([blob],'audio_gravado.webm',{type:'audio/webm'});
        const dt=new DataTransfer(); dt.items.add(file); input.files=dt.files;
        previewUrl=URL.createObjectURL(blob); preview.src=previewUrl;
        recordBar.classList.add('d-none');
        if(previewBox) previewBox.classList.remove('d-none');
      };
      recorder.start();
      if(composer) composer.classList.add('d-none');
      recordBar.classList.remove('d-none');
      startTimer();
    }catch(e){ alert('Não foi possível acessar o microfone. Verifique a permissão do navegador.'); }
  });
  stopBtn.addEventListener('click',()=>{ if(recorder&&recorder.state==='recording') recorder.stop(); });
  if(cancelBtn) cancelBtn.addEventListener('click',()=>{ if(recorder&&recorder.state==='recording'){ recorder.stop(); setTimeout(resetRecording,100); } else resetRecording(); });
  if(discardBtn) discardBtn.addEventListener('click',resetRecording);
})();
