// web/js/view_module.js (simplified)
document.addEventListener('DOMContentLoaded', async ()=>{
  const qs = new URLSearchParams(location.search);
  const moduleId = parseInt(qs.get('id'));
  if(!moduleId) return document.body.textContent = 'Kein Modul gewählt';

  const api = await waitForPywebviewApi(7000);
  const module = await api.get_module_by_id(moduleId);
  document.getElementById('moduleTitle').textContent = module ? module[1] : 'Unbekannt';

  const poolsList = document.getElementById('poolsList');
  const examList = document.getElementById('examPoolsList');
  async function loadPools(){
    poolsList.innerHTML = '';
    const pools = await api.get_pools_for_module(moduleId) || [];
    for(const p of pools){
      const id = p[0], name = p[1];
      const li = document.createElement('div');
      li.className = 'module-card';
      li.innerHTML = `<div>${escapeHtml(name)}</div><div><button data-id="${id}" class="btn add">+</button></div>`;
      poolsList.appendChild(li);
      li.querySelector('.add').addEventListener('click', ()=> examList.appendChild(document.createElement('div')).textContent = `${id}: ${name}`);
    }
  }
  // load saved config
  const cfg = await api.get_exam_config_for_module(moduleId);
  if(cfg && cfg[2]) {
    const ids = String(cfg[2]).split(',');
    // map ids -> names after pools loaded...
  }
  loadPools();
});
