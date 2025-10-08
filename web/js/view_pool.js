// web/js/view_pool.js
document.addEventListener('DOMContentLoaded', async ()=>{
  const pid = parseInt(new URLSearchParams(location.search).get('pool_id'));
  if(!pid) return;
  const api = await waitForPywebviewApi(7000);
  const tasks = await api.get_tasks_from_pool(pid) || [];
  const list = document.getElementById('taskList');
  tasks.forEach(t=>{
    const id = t[0], md = t[1];
    const el = document.createElement('div');
    el.className = 'task-list-item';
    el.innerHTML = `<div class="task-meta">ID ${id}</div>
                    <div class="task-preview">${marked.parse(md)}</div>
                    <div><button class="btn edit" data-id="${id}">Edit</button>
                          <button class="btn ghost del" data-id="${id}">Del</button></div>`;
    list.appendChild(el);
  });

  // Create / Edit modal
  const openEditor = (existingId=null, existingText='')=>{
    const modal = document.getElementById('taskEditorModal');
    const ta = document.getElementById('taskEditorTextarea');
    const preview = document.getElementById('taskEditorPreview');
    modal.classList.remove('hidden'); ta.value = existingText; ta.focus();
    ta.addEventListener('input', ()=> preview.innerHTML = marked.parse(ta.value));
    document.getElementById('saveTaskBtn').onclick = async ()=>{
      const content = ta.value.trim();
      if(!content) return alert('Bitte Text eingeben');
      if(existingId){
        await api.update_task(existingId, content);
      } else {
        await api.add_task(content, pid);
      }
      modal.classList.add('hidden');
      location.reload();
    };
  };

  list.addEventListener('click', (e)=>{
    if(e.target.matches('.edit')) {
      const id = parseInt(e.target.dataset.id);
      const t = tasks.find(x=>x[0]===id);
      openEditor(id, t[1]);
    } else if(e.target.matches('.del')) {
      if(confirm('Aufgabe löschen?')) {
        api.delete_task(parseInt(e.target.dataset.id)).then(()=> location.reload());
      }
    }
  });

  document.getElementById('newTaskBtn').addEventListener('click', ()=> openEditor(null, ''));
});
