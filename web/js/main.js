// web/js/main.js
// Single-file main UI for landing page + inline module management
(function(){
  'use strict';
  console.log('main.js (landed integrated)');

  // --- simple DOM helpers ---
  const by = id => document.getElementById(id);
  const q = sel => document.querySelector(sel);
  const escapeHtml = s => String(s||'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));

  // --- elements ---
  const modulesGrid = by('modulesGrid');
  const modulesEmpty = by('modulesEmpty');
  const moduleSearch = by('moduleSearch');
  const btnCreateModule = by('btnCreateModule');
  const emptyCreateBtn = by('emptyCreateBtn');

  const createModuleModal = by('createModuleModal');
  const newModuleName = by('newModuleName');
  const confirmCreateModule = by('confirmCreateModule');
  const cancelCreateModule = by('cancelCreateModule');
  const closeCreateModal = by('closeCreateModal');

  const createTaskModal = by('createTaskModal');
  const newTaskContent = by('newTaskContent');
  const confirmCreateTask = by('confirmCreateTask');
  const cancelCreateTask = by('cancelCreateTask');
  const closeCreateTask = by('closeCreateTask');
  const taskPoolInfo = by('taskPoolInfo');

  const confirmModal = by('confirmModal');
  const confirmMessage = by('confirmMessage');
  const confirmOk = by('confirmOk');
  const confirmCancel = by('confirmCancel');
  const confirmClose = by('confirmClose');

  const toaster = by('toaster');
  const statusDot = by('statusDot');
  const statusText = by('statusText');
  const footerStatus = by('footerStatus');

  // --- UI helpers ---
  function showToast(text, isError=false){
    if(!toaster) return;
    toaster.textContent = text;
    toaster.style.background = isError ? 'rgba(220,60,60,0.96)' : 'rgba(20,20,20,0.94)';
    toaster.classList.remove('hidden');
    clearTimeout(showToast._t);
    showToast._t = setTimeout(()=> toaster.classList.add('hidden'), 3000);
  }

  function setStatus(state, txt){
    if(!statusDot || !statusText) return;
    statusDot.classList.remove('ok','fail','checking');
    statusDot.classList.add(state || 'checking');
    const label = txt || (state==='ok' ? 'DB: verbunden' : (state==='fail' ? 'DB: nicht erreichbar' : 'DB: verbinde…'));
    statusText.textContent = label;
    if(footerStatus) footerStatus.textContent = label;
  }

  function openModal(el){
    if(!el) return; el.classList.remove('hidden'); document.body.classList.add('modal-open'); setTimeout(()=> el.querySelector('input,textarea,select,button')?.focus(), 10);
  }
  function closeModal(el){
    if(!el) return; el.classList.add('hidden'); document.body.classList.remove('modal-open');
  }

  // custom confirm returning Promise<boolean>
  function showConfirm(message, opts={okLabel:'Ja', cancelLabel:'Abbrechen'}){
    if(!confirmModal) return Promise.resolve(window.confirm(message));
    confirmMessage.textContent = message;
    confirmOk.textContent = opts.okLabel || 'Ja';
    confirmCancel.textContent = opts.cancelLabel || 'Abbrechen';
    openModal(confirmModal);
    return new Promise(resolve => {
      const ok = ()=>{ cleanup(); resolve(true); };
      const cancel = ()=>{ cleanup(); resolve(false); };
      function cleanup(){
        confirmOk.removeEventListener('click', ok);
        confirmCancel.removeEventListener('click', cancel);
        confirmClose.removeEventListener('click', cancel);
        document.removeEventListener('keydown', escHandler);
        closeModal(confirmModal);
      }
      function escHandler(e){ if(e.key === 'Escape') cancel(); }
      confirmOk.addEventListener('click', ok);
      confirmCancel.addEventListener('click', cancel);
      confirmClose.addEventListener('click', cancel);
      document.addEventListener('keydown', escHandler);
      setTimeout(()=> confirmOk.focus(), 10);
    });
  }

  // wait for pywebview.api
  function waitForApi(timeout=7000){
    const start = Date.now();
    if(window.pywebview && window.pywebview.api) return Promise.resolve(window.pywebview.api);
    return new Promise(resolve => {
      const iv = setInterval(()=>{
        if(window.pywebview && window.pywebview.api){ clearInterval(iv); resolve(window.pywebview.api); }
        if(Date.now()-start > timeout){ clearInterval(iv); resolve(null); }
      }, 120);
      document.addEventListener('pywebviewready', ()=>{
        if(window.pywebview && window.pywebview.api){ clearInterval(iv); resolve(window.pywebview.api); }
      });
    });
  }

  // cached api
  let _api = null;
  async function apiOrNull(){ if(_api) return _api; _api = await waitForApi(9000); return _api; }

  // --- core: fetch modules ---
  async function fetchModules(){
    setStatus('checking', 'Module werden geladen…');
    const api = await apiOrNull();
    if(!api){ setStatus('fail', 'Backend nicht erreichbar'); renderModules([]); return; }
    try{
      const mods = await api.get_modules();
      renderModules(Array.isArray(mods) ? mods : []);
      setStatus('ok', 'DB: verbunden');
    }catch(e){
      console.error(e); setStatus('fail', 'Fehler beim Laden'); renderModules([]);
    }
  }

  function showEmpty(yes=true){
    if(!modulesEmpty || !modulesGrid) return;
    if(yes){ modulesEmpty.classList.remove('hidden'); modulesGrid.classList.add('hidden'); }
    else { modulesEmpty.classList.add('hidden'); modulesGrid.classList.remove('hidden'); }
  }

  // --- render module cards (with inline expand area) ---
  function renderModules(modules){
    if(!modulesGrid) return;
    modulesGrid.innerHTML = '';
    if(!modules || modules.length === 0){ showEmpty(true); return; }
    showEmpty(false);

    for(const m of modules){
      const id = Array.isArray(m) ? m[0] : (m.id || m[0]);
      const name = Array.isArray(m) ? m[1] : (m.name || m[1]);

      const card = document.createElement('div');
      card.className = 'module-card';
      card.dataset.moduleId = id;
      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:flex-start;">
          <div style="flex:1; min-width:0;">
            <h3 style="margin:0 0 6px;">${escapeHtml(name)}</h3>
            <div class="meta">
              <span class="module-count">Pools: <span data-pools="${id}">–</span></span>
              <span>Aufgaben: <span data-tasks="${id}">–</span></span>
            </div>
          </div>
          <div style="display:flex; gap:8px; margin-left:12px;">
            <button class="btn btn-ghost btn-sm" data-action="toggle" data-id="${id}">Öffnen</button>
            <button class="btn btn-ghost btn-sm" data-action="add-pool" data-id="${id}">Pool +</button>
            <button class="btn btn-ghost btn-sm" data-action="delete" data-id="${id}">Löschen</button>
          </div>
        </div>

        <div class="module-expanded hidden" style="margin-top:12px; border-top:1px solid #f0f2f6; padding-top:12px;">
          <div class="pools-list"></div>
          <div style="margin-top:10px;">
            <small class="hint">Tipp: Pools anklicken, um Aufgaben zu sehen. Aufgaben können inline hinzugefügt werden.</small>
          </div>
        </div>
      `;
      modulesGrid.appendChild(card);

      // async: populate counts
      (async ()=>{
        try{
          const api = await apiOrNull(); if(!api) return;
          const pools = await api.get_pools_for_module(id);
          const poolCount = pools ? pools.length : 0;
          document.querySelector(`[data-pools="${id}"]`).textContent = poolCount;
          let taskTotal = 0;
          for(const p of (pools || [])){
            const pid = Array.isArray(p) ? p[0] : (p.id || p[0]);
            const tasks = await api.get_tasks_from_pool(pid);
            taskTotal += (tasks ? tasks.length : 0);
          }
          const tspan = document.querySelector(`[data-tasks="${id}"]`);
          tspan && (tspan.textContent = taskTotal);
        }catch(e){ console.warn('count',e); }
      })();
    }

    // attach listeners for card buttons
    modulesGrid.querySelectorAll('button').forEach(b=>{
      b.addEventListener('click', async ev=>{
        const action = b.dataset.action, id = b.dataset.id;
        if(action === 'toggle'){ toggleModuleCard(id, b); }
        if(action === 'add-pool'){ await promptAddPool(id); }
        if(action === 'delete'){ await handleDeleteModule(id); }
      });
    });
  }

  // --- expand module card and show pools / tasks ---
  async function toggleModuleCard(moduleId, btn){
    const card = modulesGrid.querySelector(`.module-card[data-module-id="${moduleId}"]`);
    if(!card) return;
    const expanded = card.querySelector('.module-expanded');
    const isHidden = expanded.classList.contains('hidden');
    if(!isHidden){ expanded.classList.add('hidden'); btn.textContent = 'Öffnen'; return; }

    // expand: load pools
    expanded.classList.remove('hidden'); btn.textContent = 'Schließen';
    const poolsList = expanded.querySelector('.pools-list');
    poolsList.innerHTML = '<div class="hint">Lade Pools…</div>';

    const api = await apiOrNull();
    if(!api){ poolsList.innerHTML = '<div class="hint">Backend nicht erreichbar</div>'; return; }
    try{
      const pools = await api.get_pools_for_module(parseInt(moduleId));
      if(!pools || pools.length === 0){ poolsList.innerHTML = '<div class="hint">Keine Pools. Nutze Pool + um einen anzulegen.</div>'; return; }
      poolsList.innerHTML = '';
      for(const p of pools){
        const pid = Array.isArray(p) ? p[0] : (p.id || p[0]);
        const pname = Array.isArray(p) ? p[1] : (p.name || p[1]);

        const poolEl = document.createElement('div');
        poolEl.style.padding = '8px';
        poolEl.style.borderRadius = '8px';
        poolEl.style.background = '#fff';
        poolEl.style.border = '1px solid #eef0f6';
        poolEl.style.marginBottom = '8px';

        poolEl.innerHTML = `
          <div style="display:flex; justify-content:space-between; align-items:center;">
            <div style="font-weight:600;">${escapeHtml(pname)}</div>
            <div style="display:flex; gap:8px;">
              <button class="btn btn-ghost btn-sm" data-action="show-tasks" data-pid="${pid}">Aufgaben</button>
              <button class="btn btn-ghost btn-sm" data-action="add-task" data-pid="${pid}">Aufgabe +</button>
              <button class="btn btn-ghost btn-sm" data-action="del-pool" data-pid="${pid}">Löschen</button>
            </div>
          </div>
          <div class="pool-tasks hidden" style="margin-top:8px;"></div>
        `;
        poolsList.appendChild(poolEl);
      }

      // attach pool-level handlers
      poolsList.querySelectorAll('button').forEach(pb=>{
        pb.addEventListener('click', async e=>{
          const act = pb.dataset.action, pid = pb.dataset.pid;
          if(act === 'show-tasks'){ await togglePoolTasks(pid, pb); }
          if(act === 'add-task'){ openAddTaskModal(pid); }
          if(act === 'del-pool'){ await handleDeletePool(pid, moduleId); }
        });
      });

    }catch(e){
      console.error(e); poolsList.innerHTML = '<div class="hint">Fehler beim Laden der Pools</div>';
    }
  }

  // show/hide tasks for given pool
  async function togglePoolTasks(poolId, btn){
    const poolEl = btn.closest('div[style]'); // our created poolEl
    if(!poolEl) return;
    const tasksDiv = poolEl.querySelector('.pool-tasks');
    if(!tasksDiv) return;
    const hidden = tasksDiv.classList.contains('hidden');
    if(!hidden){ tasksDiv.classList.add('hidden'); return; }
    tasksDiv.classList.remove('hidden'); tasksDiv.innerHTML = '<div class="hint">Lade Aufgaben…</div>';
    const api = await apiOrNull(); if(!api){ tasksDiv.innerHTML = '<div class="hint">Backend nicht erreichbar</div>'; return; }
    try{
      const tasks = await api.get_tasks_from_pool(parseInt(poolId));
      if(!tasks || tasks.length === 0){ tasksDiv.innerHTML = '<div class="hint">Keine Aufgaben in diesem Pool.</div>'; return; }
      tasksDiv.innerHTML = '';
      for(const t of tasks){
        const tid = Array.isArray(t) ? t[0] : t.id;
        const content = Array.isArray(t) ? t[1] : t.content_md || t.content;
        const item = document.createElement('div');
        item.style.borderTop = '1px dashed #f0f2f6';
        item.style.paddingTop = '8px';
        item.innerHTML = `<div style="display:flex; justify-content:space-between; align-items:flex-start;">
            <div style="white-space:pre-wrap; max-width:720px;">${escapeHtml(String(content).slice(0,400))}${String(content).length>400?'…':''}</div>
            <div style="display:flex; gap:8px; margin-left:12px;">
              <button class="btn btn-ghost btn-sm" data-action="edit-task" data-tid="${tid}">Bearbeiten</button>
              <button class="btn btn-ghost btn-sm" data-action="del-task" data-tid="${tid}">Löschen</button>
            </div>
          </div>`;
        tasksDiv.appendChild(item);
      }

      // attach task handlers (delete/edit)
      tasksDiv.querySelectorAll('button').forEach(tb=>{
        tb.addEventListener('click', async ev=>{
          const action = tb.dataset.action, tid = tb.dataset.tid;
          if(action === 'del-task'){ await handleDeleteTask(tid, poolId); }
          if(action === 'edit-task'){ showToast('Edit inline noch nicht implementiert — öffne Manage', true); }
        });
      });

    }catch(e){ console.error(e); tasksDiv.innerHTML = '<div class="hint">Fehler beim Laden</div>'; }
  }

  // --- actions: add pool (prompt) ---
  async function promptAddPool(moduleId){
    const name = prompt('Name des neuen Pools:');
    if(!name) return;
    const api = await apiOrNull(); if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await api.add_pool(name, parseInt(moduleId));
      if(res && (res.success || typeof res === 'number')){ showToast('Pool erstellt'); fetchModules(); }
      else showToast((res && res.message) || 'Fehler beim Erstellen', true);
    }catch(e){ console.error(e); showToast('Fehler beim Erstellen', true); }
  }

  // --- open add-task modal (remember pool id in dataset) ---
  let _pendingPoolForTask = null;
  function openAddTaskModal(poolId){
    _pendingPoolForTask = parseInt(poolId);
    taskPoolInfo.textContent = String(poolId);
    newTaskContent.value = '';
    openModal(createTaskModal);
  }

  // confirm create task
  confirmCreateTask && confirmCreateTask.addEventListener('click', async ()=>{
    const content = newTaskContent.value.trim();
    if(!content){ showToast('Aufgabe leer', true); return; }
    const poolId = _pendingPoolForTask;
    const api = await apiOrNull(); if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await api.add_task(content, parseInt(poolId));
      if(res && (res.success || typeof res === 'number')){ showToast('Aufgabe hinzugefügt'); closeModal(createTaskModal); fetchModules(); }
      else showToast((res && res.message) || 'Fehler beim Speichern', true);
    }catch(e){ console.error(e); showToast('Fehler beim Speichern', true); }
  });
  // cancel/close task modal
  [cancelCreateTask, closeCreateTask].forEach(el=> el && el.addEventListener('click', ()=> closeModal(createTaskModal)));

  // --- delete handlers (module/pool/task) ---
  async function handleDeleteModule(moduleId){
    const ok = await showConfirm('Modul wirklich löschen? Alle Pools & Aufgaben gehen verloren.', {okLabel:'Löschen', cancelLabel:'Abbrechen'});
    if(!ok) return;
    const api = await apiOrNull(); if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      // frontend expects API to return {success:bool, message:string} or true-ish
      const res = await (api.delete_module ? api.delete_module(parseInt(moduleId)) : api.deleteModule ? api.deleteModule(parseInt(moduleId)) : Promise.reject('delete_module not implemented'));
      if(res && (res.success || res === true)){ showToast(res.message || 'Gelöscht'); fetchModules(); }
      else showToast((res && res.message) || 'Löschfehler', true);
    }catch(e){ console.error(e); showToast('Löschen fehlgeschlagen', true); }
  }

  async function handleDeletePool(poolId, moduleId){
    const ok = await showConfirm('Pool wirklich löschen? Alle Aufgaben darin gehen verloren.');
    if(!ok) return;
    const api = await apiOrNull(); if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await (api.delete_pool ? api.delete_pool(parseInt(poolId)) : Promise.reject('delete_pool not implemented'));
      if(res && (res.success || res === true)){ showToast('Pool gelöscht'); // refresh that module card
        // find opened module card for moduleId and re-toggle to refresh
        const toggleBtn = modulesGrid.querySelector(`.module-card[data-module-id="${moduleId}"] button[data-action="toggle"]`);
        if(toggleBtn){ toggleBtn.click(); setTimeout(()=> toggleBtn.click(), 250); } else fetchModules();
      } else showToast('Fehler beim Löschen', true);
    }catch(e){ console.error(e); showToast('Fehler beim Löschen', true); }
  }

  async function handleDeleteTask(taskId, poolId){
    const ok = await showConfirm('Aufgabe wirklich löschen?');
    if(!ok) return;
    const api = await apiOrNull(); if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await (api.delete_task ? api.delete_task(parseInt(taskId)) : Promise.reject('delete_task not implemented'));
      if(res && (res.success || res === true)){ showToast('Aufgabe gelöscht'); // refresh pool tasks
        // find pool button and re-open tasks
        const poolBtn = modulesGrid.querySelector(`button[data-action="show-tasks"][data-pid="${poolId}"]`);
        if(poolBtn){ poolBtn.click(); setTimeout(()=> poolBtn.click(), 250); } else fetchModules();
      } else showToast('Fehler beim Löschen', true);
    }catch(e){ console.error(e); showToast('Fehler beim Löschen', true); }
  }

  // --- create module modal handlers ---
  if(btnCreateModule) btnCreateModule.addEventListener('click', ()=> openModal(createModuleModal));
  if(emptyCreateBtn) emptyCreateBtn.addEventListener('click', ()=> openModal(createModuleModal));
  if(cancelCreateModule) cancelCreateModule.addEventListener('click', ()=> { newModuleName.value=''; closeModal(createModuleModal); });
  if(closeCreateModal) closeCreateModal.addEventListener('click', ()=> { newModuleName.value=''; closeModal(createModuleModal); });
  if(confirmCreateModule) confirmCreateModule.addEventListener('click', async ()=>{
    const name = (newModuleName.value || '').trim();
    if(!name){ showToast('Bitte Namen eingeben', true); return; }
    const api = await apiOrNull(); if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await api.add_module(name);
      if(res && (res.success || typeof res === 'number')){ showToast('Modul erstellt'); newModuleName.value=''; closeModal(createModuleModal); fetchModules(); }
      else showToast((res && res.message) || 'Fehler', true);
    }catch(e){ console.error(e); showToast('Fehler beim Erstellen', true); }
  });

  // search filter
  if(moduleSearch) moduleSearch.addEventListener('input', ()=>{
    const qv = moduleSearch.value.trim().toLowerCase();
    document.querySelectorAll('.module-card').forEach(c=>{
      const t = c.querySelector('h3')?.textContent?.toLowerCase() || '';
      c.style.display = t.includes(qv) ? '' : 'none';
    });
  });

  // keyboard: Enter creates module when modal open
  newModuleName && newModuleName.addEventListener('keydown', e=>{ if(e.key==='Enter') confirmCreateModule.click(); });

  // initial boot: try to connect to API then fetch
  (async ()=>{
    setStatus('checking','Warte auf Backend…');
    const api = await waitForApi(9000);
    if(api){ _api = api; setStatus('ok','DB: verbunden'); }
    else setStatus('fail','Backend nicht erreichbar');
    fetchModules();
  })();

  // expose for debugging
  window.fetchModules = fetchModules;
})();
