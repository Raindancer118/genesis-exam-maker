// web/js/main.js
// Robust init for pywebview-based UI
// - binds UI handlers immediately (so buttons/modals respond)
// - waits for pywebview.api and then performs backend calls
// - exposes window.fetchModules for console debugging

console.log('main.js running — startup');
window.mainJsLoaded = true;

document.addEventListener('DOMContentLoaded', () => {
  // ---- helpers ----
  function by(id){ return document.getElementById(id); }
  function escapeHtml(s){ return String(s || '').replace(/[&<>"']/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }

  function showToast(text, isError=false){
    const t = by('toaster');
    if(!t) return;
    t.textContent = text;
    t.style.background = isError ? 'rgba(220,60,60,0.96)' : 'rgba(20,20,20,0.94)';
    t.classList.remove('hidden');
    clearTimeout(showToast._timer);
    showToast._timer = setTimeout(()=> t.classList.add('hidden'), 3000);
  }

  function setStatus(text, state){
    const statusText = by('statusText');
    const statusDot = by('statusDot');
    const footer = by('footerStatus');
    let mappedText = String(text || '');
    const lower = mappedText.toLowerCase();

    if (lower.includes('backend') || lower.includes('module')) {
      if (state === 'ok' || lower.includes('erreich')) mappedText = 'DB: verbunden';
      else if (state === 'checking' || lower.includes('warte') || lower.includes('lade') || lower.includes('prüf')) mappedText = 'DB: verbinde…';
      else if (state === 'fail' || lower.includes('fehler') || lower.includes('nicht erreichbar')) mappedText = 'DB: nicht erreichbar';
    } else {
      if (!mappedText.toLowerCase().startsWith('db:') && (state === 'ok' || state === 'fail' || state === 'checking')) {
        if (state === 'ok') mappedText = 'DB: verbunden';
        else if (state === 'checking') mappedText = 'DB: verbinde…';
        else if (state === 'fail') mappedText = 'DB: nicht erreichbar';
      }
    }

    if(statusText) statusText.textContent = mappedText;
    if(footer) footer.textContent = mappedText;
    if(statusDot){
      statusDot.classList.remove('ok','fail','checking');
      if(state==='ok') statusDot.classList.add('ok');
      else if(state==='fail') statusDot.classList.add('fail');
      else statusDot.classList.add('checking');
    }
  }

  async function waitForPywebviewApi(timeoutMs=7000){
    const start = Date.now();
    if(window.pywebview && window.pywebview.api) return window.pywebview.api;
    return new Promise(resolve => {
      const interval = setInterval(()=>{
        if(window.pywebview && window.pywebview.api){
          clearInterval(interval);
          resolve(window.pywebview.api);
        } else if(Date.now()-start > timeoutMs){
          clearInterval(interval);
          resolve(null);
        }
      }, 100);
      document.addEventListener('pywebviewready', ()=>{
        if(window.pywebview && window.pywebview.api){
          clearInterval(interval);
          resolve(window.pywebview.api);
        }
      });
    });
  }

  // ---- DOM references ----
  const modulesGrid = by('modulesGrid');
  const modulesEmpty = by('modulesEmpty');
  const searchInput = by('moduleSearch');

  // modals + controls
  const btnCreateModule = by('btnCreateModule');
  const btnManage = by('btnManage');
  const btnCreateExam = by('btnCreateExam');
  const btnImportExport = by('btnImportExport');

  const createModuleModal = by('createModuleModal');
  const newModuleName = by('newModuleName');
  const confirmCreateModule = by('confirmCreateModule');
  const cancelCreateModule = by('cancelCreateModule');
  const closeCreateModal = by('closeCreateModal');

  const createPoolModal = by('createPoolModal');
  const newPoolName = by('newPoolName');
  const confirmCreatePool = by('confirmCreatePool');
  const cancelCreatePool = by('cancelCreatePool');
  const closeCreatePool = by('closeCreatePool');
  const poolModuleIdDisplay = by('poolModuleIdDisplay');

  const createExamModal = by('createExamModal');
  const selectModule = by('selectModule');
  const examFilename = by('examFilename');
  const confirmCreateExam = by('confirmCreateExam');
  const cancelCreateExam = by('cancelCreateExam');
  const examStatus = by('examStatus');

  const toaster = by('toaster');
  const emptyCreateBtn = by('emptyCreateBtn');

  // ---- UI-only bindings (work even if backend not ready) ----
  function openModal(el){ if(!el) return; el.classList.remove('hidden'); el.querySelector('input,textarea,select')?.focus(); }
  function closeModal(el){ if(!el) return; el.classList.add('hidden'); }

  if(btnCreateModule) btnCreateModule.addEventListener('click', ()=> openModal(createModuleModal));
  if(emptyCreateBtn) emptyCreateBtn.addEventListener('click', ()=> openModal(createModuleModal));
  if(btnCreateExam) btnCreateExam.addEventListener('click', async ()=>{
    await populateModuleSelect(); openModal(createExamModal);
  });
  if(btnImportExport) btnImportExport.addEventListener('click', ()=> window.location.href = 'import_export.html');

  if(cancelCreateModule) cancelCreateModule.addEventListener('click', ()=> { closeModal(createModuleModal); newModuleName.value=''; });
  if(closeCreateModal) closeCreateModal.addEventListener('click', ()=> { closeModal(createModuleModal); newModuleName.value=''; });
  if(confirmCreateModule) confirmCreateModule.addEventListener('click', async ()=>{
    const name = (newModuleName.value || '').trim();
    if(!name){ showToast('Bitte Namen eingeben', true); return; }
    await createModule(name);
  });

  // Pool modal handlers (replaces prompt())
  let _currentModuleForPool = null;
  if(cancelCreatePool) cancelCreatePool.addEventListener('click', ()=> { closeModal(createPoolModal); newPoolName.value=''; _currentModuleForPool = null; poolModuleIdDisplay.textContent = '—'; });
  if(closeCreatePool) closeCreatePool.addEventListener('click', ()=> { closeModal(createPoolModal); newPoolName.value=''; _currentModuleForPool = null; poolModuleIdDisplay.textContent = '—'; });
  if(confirmCreatePool) confirmCreatePool.addEventListener('click', async ()=>{
    const poolName = (newPoolName.value || '').trim();
    if(!_currentModuleForPool){ showToast('Kein Modul gewählt', true); closeModal(createPoolModal); return; }
    if(!poolName){ showToast('Bitte einen Pool-Namen eingeben', true); return; }
    const api = await getApiOrNull();
    if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await api.add_pool(poolName, parseInt(_currentModuleForPool));
      if(res && res.success){
        showToast('Pool erstellt');
        closeModal(createPoolModal);
        newPoolName.value = '';
        _currentModuleForPool = null;
        poolModuleIdDisplay.textContent = '—';
        await fetchModules();
      } else {
        showToast(res && res.message ? res.message : 'Fehler beim Erstellen', true);
      }
    }catch(e){
      console.error('createPool error', e);
      showToast('Fehler beim Erstellen', true);
    }
  });

  // Create Exam modal
  if(cancelCreateExam) cancelCreateExam.addEventListener('click', ()=> { closeModal(createExamModal); examStatus.textContent=''; });
  if(confirmCreateExam) confirmCreateExam.addEventListener('click', async ()=>{
    const moduleId = selectModule?.value;
    const filename = (examFilename?.value || '').trim();
    if(!moduleId){ showToast('Bitte Modul auswählen', true); return; }
    await buildExam(parseInt(moduleId), filename);
  });

  // allow Enter key in newModuleName to submit
  newModuleName && newModuleName.addEventListener('keydown', (e)=>{ if(e.key==='Enter') confirmCreateModule?.click(); });
  newPoolName && newPoolName.addEventListener('keydown', (e)=>{ if(e.key==='Enter') confirmCreatePool?.click(); });

  // ---- API wrapper that waits for API if necessary ----
  let _api = null; // cached api
  async function getApiOrNull(){
    if(_api) return _api;
    _api = await waitForPywebviewApi(7000);
    return _api;
  }

  async function createModule(name){
    const api = await getApiOrNull();
    if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await api.add_module(name);
      showToast(res && res.success ? 'Modul erstellt' : (res.message || 'Fehler'));
      closeModal(createModuleModal);
      newModuleName.value = '';
      await fetchModules();
    }catch(e){
      console.error('createModule error', e);
      showToast('Fehler beim Erstellen', true);
    }
  }

  async function buildExam(moduleId, filename){
    const api = await getApiOrNull();
    if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      examStatus.textContent = 'Generiere PDF...';
      const res = await api.build_exam_for_module(moduleId, filename || '');
      if(res && res.success){
        examStatus.textContent = 'Fertig: ' + res.path;
        showToast('Klausur erstellt', false);
        setTimeout(()=> closeModal(createExamModal), 800);
      } else {
        examStatus.textContent = 'Fehler: ' + (res && res.message ? res.message : 'unknown');
        showToast('Fehler bei der Erstellung', true);
      }
    } catch(e){
      console.error('buildExam error', e);
      examStatus.textContent = 'Fehler beim Generieren';
      showToast('Fehler beim Generieren', true);
    }
  }

  // ---- modules rendering / counts ----
  function showEmpty(yes=true){
    if(!modulesEmpty || !modulesGrid) return;
    if(yes){ modulesEmpty.classList.remove('hidden'); modulesGrid.classList.add('hidden'); }
    else { modulesEmpty.classList.add('hidden'); modulesGrid.classList.remove('hidden'); }
  }

  function renderModules(modules){
    if(!modulesGrid) return;
    modulesGrid.innerHTML = '';
    if(!modules || modules.length===0){ showEmpty(true); return; }
    showEmpty(false);

    if(selectModule) selectModule.innerHTML = '<option value="">-- auswählen --</option>';

    for(const m of modules){
      const id = Array.isArray(m) ? m[0] : (m.id || m[0]);
      const name = Array.isArray(m) ? m[1] : (m.name || m[1]);
      const card = document.createElement('div');
      card.className = 'module-card';
      card.innerHTML = `
        <div class="content">
          <h3>${escapeHtml(name)}</h3>
          <div class="meta">
            <span class="module-count">Pools: <span data-pools="${id}">–</span></span>
            <span>Aufgaben: <span data-tasks="${id}">–</span></span>
          </div>
        </div>
        <div class="actions">
          <button class="btn btn-ghost" data-action="open" data-id="${id}">Öffnen</button>
          <button class="btn btn-ghost" data-action="add-pool" data-id="${id}">Pool +</button>
          <button class="btn btn-ghost" data-action="delete" data-id="${id}">Löschen</button>
        </div>
      `;
      modulesGrid.appendChild(card);

      if(selectModule){
        const opt = document.createElement('option'); opt.value = id; opt.textContent = name;
        selectModule.appendChild(opt);
      }

      // async counts
      (async ()=>{
        try{
          const api = await getApiOrNull();
          if(!api) return;
          const pools = await api.get_pools_for_module(id);
          const poolCount = pools ? pools.length : 0;
          const poolSpan = document.querySelector(`[data-pools="${id}"]`);
          poolSpan && (poolSpan.textContent = poolCount);

          let taskTotal = 0;
          for(const p of (pools || [])){
            const pid = Array.isArray(p) ? p[0] : p.id;
            const tasks = await api.get_tasks_from_pool(pid);
            taskTotal += (tasks ? tasks.length : 0);
            const tspan = document.querySelector(`[data-tasks="${id}"]`);
            tspan && (tspan.textContent = taskTotal);
          }
        }catch(e){
          console.warn('count error', e);
        }
      })();
    }

    // attach handlers
    modulesGrid.querySelectorAll('button').forEach(b=>{
      b.addEventListener('click', async ()=>{
        const action = b.dataset.action;
        const id = b.dataset.id;
        if(action === 'open') window.location.href = `view_module.html?id=${encodeURIComponent(id)}`;
        if(action === 'add-pool'){
          // open our custom modal instead of prompt()
          _currentModuleForPool = id;
          if(poolModuleIdDisplay) poolModuleIdDisplay.textContent = id;
          if(newPoolName) newPoolName.value = '';
          openModal(createPoolModal);
        }
        if(action === 'delete'){
          const api = await getApiOrNull();
          if(!api){ showToast('Backend nicht erreichbar', true); return; }
          const ok = confirm(`Modul wirklich löschen? ID ${id}`); // quick fallback; we also have a nicer confirm modal you can wire up
          if(!ok) return;
          try{
            await api.delete_module(parseInt(id));
            showToast('Löschen erfolgreich');
            fetchModules();
          }catch(e){
            console.error('delete module', e);
            showToast('Fehler beim Löschen', true);
          }
        }
      });
    });
  }

  // ---- populate module select for exam modal ----
  async function populateModuleSelect(){
    if(!selectModule) return;
    selectModule.innerHTML = '<option value="">-- auswählen --</option>';
    const api = await getApiOrNull();
    if(!api) return;
    try{
      const mods = await api.get_modules();
      for(const m of (mods || [])){
        const id = Array.isArray(m) ? m[0] : (m.id || m[0]);
        const name = Array.isArray(m) ? m[1] : (m.name || m[1]);
        const opt = document.createElement('option'); opt.value = id; opt.textContent = name;
        selectModule.appendChild(opt);
      }
    }catch(e){ console.warn(e); }
  }

  // ---- fetchModules (public) ----
  async function fetchModules(){
    setStatus('Warte auf Backend...', 'checking');
    const api = await getApiOrNull();
    if(!api){ setStatus('Backend nicht erreichbar', 'fail'); showEmpty(true); return; }
    try{
      setStatus('Module werden geladen...', 'checking');
      const modules = await api.get_modules();
      renderModules(Array.isArray(modules) ? modules : []);
      setStatus('Backend: erreichbar', 'ok');
    }catch(e){
      console.error('fetchModules error', e);
      setStatus('Fehler beim Laden', 'fail');
      showEmpty(true);
    }
  }

  // expose for console/debugging
  window.fetchModules = fetchModules;
  window.openCreateModule = ()=> openModal(createModuleModal);

  // search filter
  if(searchInput) searchInput.addEventListener('input', ()=>{
    const q = searchInput.value.trim().toLowerCase();
    modulesGrid.querySelectorAll('.module-card').forEach(c=>{
      const t = c.querySelector('h3')?.textContent?.toLowerCase() || '';
      c.style.display = t.includes(q) ? '' : 'none';
    });
  });

  // start: try to fetch modules (will wait for api short time)
  fetchModules();

  // Auto-retry background if backend comes later
  (async ()=>{
    const api = await waitForPywebviewApi(15000);
    if(api){
      console.log('pywebview.api now available (background)');
      _api = api;
      fetchModules();
    } else {
      console.warn('pywebview.api not available after retries');
      setStatus('Backend nicht erreichbar', 'fail');
    }
  })();

});
