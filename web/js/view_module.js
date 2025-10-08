// web/js/view_module.js
// JS für die Modul-Detailseite: läd Modul, Pools und Aufgaben,
// verbindet die vorhandenen Modals mit API-Aufrufen (pywebview).

console.log("view_module.js loaded");

document.addEventListener('DOMContentLoaded', () => {
  function by(id){ return document.getElementById(id); }
  function qs(sel, root=document){ return root.querySelector(sel); }
  function showToast(msg, isError=false){
    const t = by('toaster'); if(!t) return;
    t.textContent = msg; t.style.background = isError ? 'rgba(220,60,60,0.96)' : 'rgba(20,20,20,0.94)';
    t.classList.remove('hidden'); clearTimeout(showToast._t);
    showToast._t = setTimeout(()=> t.classList.add('hidden'), 3000);
  }

  // --- util: get module id from querystring ---
  function getModuleId(){
    const p = new URLSearchParams(window.location.search);
    return p.get('id') || '';
  }

  // --- API wrapper that waits for pywebview.api ---
  async function getApi(){
    if(window.pywebview && window.pywebview.api) return window.pywebview.api;
    // short wait
    for(let i=0;i<50;i++){
      if(window.pywebview && window.pywebview.api) return window.pywebview.api;
      await new Promise(r=>setTimeout(r,50));
    }
    return null;
  }

  // DOM refs
  const moduleTitle = by('moduleTitle');
  const moduleName = by('moduleName');
  const moduleMeta = by('moduleMeta');
  const poolCount = by('poolCount');
  const taskCount = by('taskCount');
  const poolsGrid = by('poolsGrid');
  const poolsEmpty = by('poolsEmpty');
  const tasksSection = by('taskListSection');
  const tasksContainer = by('tasksContainer');
  const tasksEmpty = by('tasksEmpty');
  const tasksTitle = by('tasksTitle');
  const tasksSubtitle = by('tasksSubtitle');

  const btnBack = by('btnBack');
  const btnAddPool = by('btnAddPool');
  const btnAddTask = by('btnAddTask');

  // modals
  const createPoolModal = by('createPoolModal');
  const newPoolName = by('newPoolName');
  const confirmCreatePool = by('confirmCreatePool');
  const cancelCreatePool = by('cancelCreatePool');
  const closeCreatePool = by('closeCreatePool');
  const poolModuleIdDisplay = by('poolModuleIdDisplay');

  const createTaskModal = by('createTaskModal');
  const taskPoolInfo = by('taskPoolInfo');
  const newTaskContent = by('newTaskContent');
  const confirmCreateTask = by('confirmCreateTask');
  const cancelCreateTask = by('cancelCreateTask');
  const closeCreateTask = by('closeCreateTask');

  const confirmModal = by('confirmModal');
  const confirmTitle = by('confirmTitle');
  const confirmMessage = by('confirmMessage');
  const confirmOk = by('confirmOk');
  const confirmCancel = by('confirmCancel');
  const confirmClose = by('confirmClose');

  // local state
  let moduleId = getModuleId();
  let pools = []; // [{id, name}]
  let currentPoolId = null;
  let editingTaskId = null;

  // navigation
  btnBack && btnBack.addEventListener('click', ()=> window.location.href = 'index.html');

  // show/hide modal helpers
  const openModal = (el) => el && el.classList.remove('hidden');
  const closeModal = (el) => el && el.classList.add('hidden');

  // wire pool modal buttons
  confirmCreatePool && confirmCreatePool.addEventListener('click', async ()=>{
    const name = (newPoolName.value || '').trim();
    if(!name){ showToast('Bitte Namen eingeben', true); return; }
    const api = await getApi();
    if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      const res = await api.add_pool(name, parseInt(moduleId));
      if(res && res.success){ showToast('Pool angelegt'); newPoolName.value=''; closeModal(createPoolModal); await reloadPools(); }
      else showToast(res && res.message ? res.message : 'Fehler', true);
    }catch(e){ console.error(e); showToast('Fehler', true); }
  });
  cancelCreatePool && cancelCreatePool.addEventListener('click', ()=> closeModal(createPoolModal));
  closeCreatePool && closeCreatePool.addEventListener('click', ()=> closeModal(createPoolModal));

  // wire add pool button
  btnAddPool && btnAddPool.addEventListener('click', ()=>{
    poolModuleIdDisplay && (poolModuleIdDisplay.textContent = moduleId);
    openModal(createPoolModal);
    newPoolName && newPoolName.focus();
  });

  // wire task modal (create/edit)
  function openTaskModal(poolId, poolName, taskId=null, existingContent=''){
    currentPoolId = poolId;
    editingTaskId = taskId;
    taskPoolInfo && (taskPoolInfo.textContent = poolName || poolId);
    newTaskContent && (newTaskContent.value = existingContent || '');
    openModal(createTaskModal);
    newTaskContent && newTaskContent.focus();
  }

  confirmCreateTask && confirmCreateTask.addEventListener('click', async ()=>{
    const content = (newTaskContent.value || '').trim();
    if(!content){ showToast('Aufgabe darf nicht leer sein', true); return; }
    const api = await getApi();
    if(!api){ showToast('Backend nicht erreichbar', true); return; }
    try{
      if(editingTaskId){
        // updateTask - ensure API supports this (see instructions)
        if(typeof api.update_task === 'function'){
          const res = await api.update_task(editingTaskId, content);
          if(res && res.success){ showToast('Aufgabe aktualisiert'); closeModal(createTaskModal); await reloadTasks(currentPoolId); }
          else showToast(res && res.message ? res.message : 'Fehler beim Speichern', true);
        } else {
          // fallback: delete + create (not ideal)
          await api.delete_task(editingTaskId);
          const res = await api.add_task(content, parseInt(currentPoolId));
          if(res && res.success){ showToast('Aufgabe gespeichert (fallback)'); closeModal(createTaskModal); await reloadTasks(currentPoolId); }
          else showToast('Fehler beim Ersetzen', true);
        }
      } else {
        const res = await api.add_task(content, parseInt(currentPoolId));
        if(res && res.success){ showToast('Aufgabe angelegt'); closeModal(createTaskModal); await reloadTasks(currentPoolId); }
        else showToast(res && res.message ? res.message : 'Fehler', true);
      }
    }catch(e){ console.error(e); showToast('Fehler', true); }
  });
  cancelCreateTask && cancelCreateTask.addEventListener('click', ()=> closeModal(createTaskModal));
  closeCreateTask && closeCreateTask.addEventListener('click', ()=> closeModal(createTaskModal));

  // confirm modal utilities
  function askConfirm(title, message){
    return new Promise((resolve)=>{
      confirmTitle && (confirmTitle.textContent = title || 'Bestätigung');
      confirmMessage && (confirmMessage.textContent = message || 'Bist du sicher?');
      openModal(confirmModal);
      const onOk = ()=> { cleanup(); resolve(true); };
      const onCancel = ()=> { cleanup(); resolve(false); };
      function cleanup(){
        confirmOk.removeEventListener('click', onOk);
        confirmCancel.removeEventListener('click', onCancel);
        confirmClose.removeEventListener('click', onCancel);
        closeModal(confirmModal);
      }
      confirmOk.addEventListener('click', onOk);
      confirmCancel.addEventListener('click', onCancel);
      confirmClose.addEventListener('click', onCancel);
    });
  }

  // helper to build a pool-card DOM element
  function poolCard(pool){
    const div = document.createElement('div');
    div.className = 'module-card pool-card';
    div.innerHTML = `
      <div class="content">
        <h3>${escapeHtml(pool[1] || pool.name || '')}</h3>
        <div class="meta"><span class="hint">ID: ${pool[0] || pool.id}</span><span class="hint pools-tasks" data-pid="${pool[0]||pool.id}">—</span></div>
      </div>
      <div class="actions">
        <button class="btn btn-ghost btn-sm btn-open-pool" data-id="${pool[0]||pool.id}">Öffnen</button>
        <button class="btn btn-sm btn-ghost btn-edit-pool" data-id="${pool[0]||pool.id}">Bearbeiten</button>
        <button class="btn btn-sm btn-ghost btn-delete-pool" data-id="${pool[0]||pool.id}">Löschen</button>
      </div>
    `;
    return div;
  }

  // escape helper
  function escapeHtml(s){ return String(s||'').replace(/[&<>"']/g, m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m])); }

  // load module + pools
  async function loadModule(){
    const api = await getApi();
    if(!api){ showToast('Backend nicht erreichbar', true); updateStatus('DB: nicht erreichbar', 'fail'); return; }
    try{
      const mod = await api.get_module_by_id(parseInt(moduleId));
      if(!mod){ moduleName.textContent='Unbekannt'; moduleTitle.textContent='Module'; moduleMeta.textContent = `ID: ${moduleId}`; return; }
      moduleName.textContent = mod[1] || mod.name || '—';
      moduleTitle.textContent = mod[1] || mod.name || '—';
      moduleMeta.textContent = `ID: ${mod[0] || mod.id}`;
      updateStatus('DB: verbunden', 'ok');
    }catch(e){ console.error(e); updateStatus('DB: nicht erreichbar', 'fail'); }
    await reloadPools();
  }

  async function reloadPools(){
    const api = await getApi();
    if(!api) return;
    try{
      poolsGrid.innerHTML = '';
      pools = await api.get_pools_for_module(parseInt(moduleId));
      if(!pools || pools.length===0){ poolsEmpty && poolsEmpty.classList.remove('hidden'); poolCount.textContent = 0; return; }
      poolsEmpty && poolsEmpty.classList.add('hidden');
      poolCount.textContent = pools.length;
      // compute total tasks
      let totalTasks = 0;
      for(const p of pools){
        const pid = Array.isArray(p) ? p[0] : p.id;
        const tasks = await api.get_tasks_from_pool(pid);
        totalTasks += tasks ? tasks.length : 0;
        const card = poolCard(p);
        poolsGrid.appendChild(card);
      }
      taskCount.textContent = totalTasks;
      // attach handlers
      poolsGrid.querySelectorAll('.btn-open-pool').forEach(b=>{
        b.addEventListener('click', async (ev)=>{
          const pid = b.dataset.id;
          await reloadTasks(pid);
        });
      });
      poolsGrid.querySelectorAll('.btn-edit-pool').forEach(b=>{
        b.addEventListener('click', (ev)=>{
          const pid = b.dataset.id;
          // simple inline rename prompt (could be modal)
          const old = pools.find(x => (Array.isArray(x) ? x[0] : x.id) == pid);
          const oldName = Array.isArray(old) ? old[1] : (old && old.name);
          const newName = prompt("Neuer Pool-Name:", oldName || '');
          if(newName && newName.trim()){
            // We don't have an API update_pool right now; fallback: create new & maybe delete old is not ideal.
            showToast('Pool-Umbenennung noch nicht unterstützt (implementiere update_pool API)', true);
          }
        });
      });
      poolsGrid.querySelectorAll('.btn-delete-pool').forEach(b=>{
        b.addEventListener('click', async ()=>{
          const pid = b.dataset.id;
          const ok = await askConfirm('Pool löschen', `Möchtest du den Pool ID ${pid} wirklich löschen?`);
          if(!ok) return;
          const api = await getApi();
          try{
            const res = await api.delete_pool(parseInt(pid));
            if(res && res.success){ showToast('Pool gelöscht'); await reloadPools(); await reloadTasks(null); }
            else showToast(res && res.message ? res.message : 'Fehler', true);
          }catch(e){ console.error(e); showToast('Fehler', true); }
        });
      });
    }catch(e){ console.error(e); showToast('Fehler beim Laden der Pools', true); }
  }

  // tasks loading for a pool
  async function reloadTasks(poolId){
    tasksContainer.innerHTML = '';
    tasksSection.style.display = 'none';
    tasksEmpty.classList.add('hidden');
    tasksTitle.textContent = 'Aufgaben im Pool';
    tasksSubtitle.textContent = '';
    if(!poolId) return;
    const api = await getApi();
    if(!api) { showToast('Backend nicht erreichbar', true); return; }
    try{
      const tasks = await api.get_tasks_from_pool(parseInt(poolId));
      if(!tasks || tasks.length===0){ tasksEmpty.classList.remove('hidden'); tasksSection.style.display = 'block'; return; }
      tasksSection.style.display = 'block';
      tasksTitle.textContent = `Aufgaben — Pool ${poolId}`;
      tasksSubtitle.textContent = `${tasks.length} Aufgaben`;
      tasks.forEach(t=>{
        const div = document.createElement('div');
        div.className = 'task-list task';
        div.style.marginBottom = '10px';
        div.innerHTML = `
          <div style="display:flex; justify-content:space-between; gap:8px;">
            <div style="flex:1;">
              <div class="hint">ID: ${t.id}</div>
              <div style="margin-top:6px;">${t.raw_md.slice(0,300).replace(/\n/g,'<br>')}</div>
            </div>
            <div style="display:flex; flex-direction:column; gap:8px; margin-left:12px;">
              <button class="btn btn-sm btn-ghost btn-edit-task" data-id="${t.id}">Bearbeiten</button>
              <button class="btn btn-sm btn-ghost btn-delete-task" data-id="${t.id}">Löschen</button>
            </div>
          </div>
        `;
        tasksContainer.appendChild(div);
      });

      // attach task handlers
      tasksContainer.querySelectorAll('.btn-edit-task').forEach(b=>{
        b.addEventListener('click', async ()=>{
          const tid = b.dataset.id;
          // find raw content
          const task = (await api.get_tasks_from_pool(parseInt(poolId))).find(x => x.id == tid);
          const content = task ? task.raw_md : '';
          openTaskModal(poolId, `ID:${poolId}`, parseInt(tid), content);
        });
      });
      tasksContainer.querySelectorAll('.btn-delete-task').forEach(b=>{
        b.addEventListener('click', async ()=>{
          const tid = b.dataset.id;
          const ok = await askConfirm('Aufgabe löschen', `Aufgabe ID ${tid} endgültig löschen?`);
          if(!ok) return;
          try{
            const res = await api.delete_task(parseInt(tid));
            if(res && res.success){ showToast('Aufgabe gelöscht'); await reloadTasks(poolId); await reloadPools(); }
            else showToast(res && res.message ? res.message : 'Fehler', true);
          }catch(e){ console.error(e); showToast('Fehler', true); }
        });
      });

    }catch(e){ console.error(e); showToast('Fehler beim Laden der Aufgaben', true); }
  }

  // Add-task button (opens createTaskModal; user chooses pool via dropdown? For quickness: if exactly one pool, preselect it)
  btnAddTask && btnAddTask.addEventListener('click', async ()=>{
    if(!pools || pools.length===0){ showToast('Bitte zuerst einen Pool anlegen', true); return; }
    // pick first pool if none selected
    const p = pools[0];
    const pid = Array.isArray(p) ? p[0] : p.id;
    openTaskModal(pid, Array.isArray(p)?p[1]:p.name);
  });

  // status dot helper
  function updateStatus(text, state){
    const dot = by('statusDot'), st = by('statusText'), footer = by('footerStatus');
    if(st) st.textContent = text;
    if(footer) footer.textContent = text;
    if(dot){
      dot.classList.remove('ok','fail','checking');
      if(state==='ok') dot.classList.add('ok');
      else if(state==='fail') dot.classList.add('fail');
      else dot.classList.add('checking');
    }
  }

  // initial load:
  if(!moduleId){ showToast('Keine Modul-ID in URL'); } else { loadModule(); }

});
