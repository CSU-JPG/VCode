const fetchJSON = p => fetch(p).then(r=>r.json()).catch(()=>({}));
const fetchText = p => fetch(p).then(r => r.text()).catch(() => "");
const parseJSONL = (text) => {
  if (!text || !text.trim()) return [];
  return text.trim().split('\n').filter(Boolean).map(line => JSON.parse(line));
};
function getMmmuImagePath(id) {
    if (!id || typeof id !== 'string') return '';
    const parts = id.split('_');
    if (parts.length < 2) return '';
    const subtaskName = parts.slice(1, -1).join('_'); 
    const filename = `${id}_img1.png`;
    return `generated_imgs/${subtaskName}/${filename}`;
}
function createTabbedModalHTML(tabs) {
    const tabButtons = Object.keys(tabs).map((key, index) => 
        `<button class="tab-button ${index === 0 ? 'active' : ''}" onclick="switchTab(this, '${key}')">${tabs[key].label}</button>`
    ).join('');
    const tabContents = Object.keys(tabs).map((key, index) => 
        `<div id="tab-${key}" class="tab-content ${index === 0 ? 'active' : ''}">${tabs[key].content}</div>`
    ).join('');
    return `<div class="border-b border-gray-200">${tabButtons}</div><div>${tabContents}</div>`;
}
function switchTab(button, tabId) {
    const tabContainer = button.closest('.modal-content');
    tabContainer.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
    tabContainer.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    button.classList.add('active');
    tabContainer.querySelector(`#tab-${tabId}`).classList.add('active');
}

function modal(title, html){
  const bg = document.createElement('div');
  bg.className = 'modal-bg';
  bg.innerHTML = `<div class='bg-white rounded-xl p-6 max-h-[90vh] max-w-[90vw] overflow-auto shadow-xl modal-content'>
     <h2 class='font-semibold text-lg mb-4'>${title}</h2>${html}
     <div class='text-right mt-6'><button class='px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors' onclick='this.closest(".modal-bg").remove()'>Close</button></div>
   </div>`;
  document.body.appendChild(bg);
}
function clipCell(text, label){
  const td = document.createElement('td');
  td.textContent = text;
  td.className   = 'px-3 py-3 clip-text text-gray-700';
  td.addEventListener('click', ()=> modal(label, `<p class="whitespace-pre-wrap text-gray-800">${text}</p>`));
  return td;
}
function scoreCell(score, pred){
  const td = document.createElement('td');
  td.textContent = score ?? '—';
  td.className   = 'px-3 py-3 text-center cursor-pointer font-medium';
  td.addEventListener('click', ()=> modal('Prediction', `<p class="whitespace-pre-wrap text-gray-800">${pred ?? '—'}</p>`));
  if(score==1||score==='1.0') td.classList.add('text-emerald-600', 'bg-emerald-50');
  else if(score==0||score==='0.0') td.classList.add('text-rose-600', 'bg-rose-50');
  else td.classList.add('text-gray-400');
  return td;
}

function imgCell(src, score, pred, textContent) {
    const td = document.createElement('td');
    td.className = 'p-1.5 align-top'; 
    const container = document.createElement('div');
    container.className = 'image-cell-container';
    const wrapper = document.createElement('div');
    wrapper.className = 'image-wrapper';
    const img = document.createElement('img');
    img.src = src;
    wrapper.appendChild(img);
    container.appendChild(wrapper);
    if (score !== null && score !== undefined) {
        const scoreBar = document.createElement('div');
        scoreBar.className = 'score-bar';
        
        if (score == 1) {
            scoreBar.classList.add('score-bar-correct');
        } else if (score > 0 && score < 1) {
            scoreBar.classList.add('score-bar-partial');
        } else if (score == 0) {
            scoreBar.classList.add('score-bar-incorrect');
        } else {
            scoreBar.classList.add('score-bar-neutral');
        }
        
        scoreBar.textContent = Number(score).toFixed(1);
        container.appendChild(scoreBar);
    }

    container.addEventListener('click', () => {
        const tabs = {
            image: { label: 'Image', content: `<img src='${src}' class='max-w-full h-auto rounded-lg'>` },
            prediction: { label: 'Prediction', content: `<pre class="whitespace-pre-wrap text-gray-800 bg-gray-50 p-4 rounded-md text-sm">${pred || '—'}</pre>` }
        };

        if (textContent) {
            tabs.generation = { label: 'Generation Details', content: `<pre class="whitespace-pre-wrap text-gray-800 bg-gray-50 p-4 rounded-md text-sm">${textContent}</pre>` };
        }

        modal('Details', createTabbedModalHTML(tabs));
    });

    td.appendChild(container);
    return td;
}
function showLoader(show) {
    const container = document.getElementById('tableContainer');
    let overlay = container.querySelector('.loader-overlay');
    if (show) {
        if (!overlay) {
            overlay = document.createElement('div');
            overlay.className = 'loader-overlay';
            overlay.innerHTML = '<div class="loader"></div>';
            container.appendChild(overlay);
        }
    } else {
        overlay?.remove();
    }
}
function handleBenchmarkSwitch() {
    const benchmark = document.querySelector('input[name="benchmark"]:checked').value;
    const modelSel = document.getElementById('modelSel');
    modelSel.innerHTML = '';
    let inferenceModels, capabilities;

    if (benchmark === 'mmvet') {
        inferenceModels = { 'g4omini': 'GPT-4o-mini', '7B': 'Qwen2.5-VL-7B', '3B': 'Qwen2.5-VL-3B',  };
        capabilities = {
            "ocr": "OCR", "math": "Math", "spat": "Spatial",
            "rec": "Recognition", "know": "Knowledge", "gen": "Generation"
        };
    } else if (benchmark === 'cvbench') {
        inferenceModels = CVBENCH_CONFIG.inferenceModels;
        capabilities = CVBENCH_CONFIG.capabilities;
    } else if (benchmark === 'mmmu') {
        inferenceModels = MMMU_CONFIG.inferenceModels;
        capabilities = Object.fromEntries(
        MMMU_CONFIG.subtasks.map(task => [task, task.replace(/_/g, ' ')])
        );
    }
    for (const [key, label] of Object.entries(inferenceModels)) {
        modelSel.add(new Option(label, key));
    }
    const capFilter = document.getElementById('capabilityFilter');
    capFilter.innerHTML = '';
    capFilter.add(new Option('All Capabilities', 'all'));
    if (capabilities) {
        for (const [key, label] of Object.entries(capabilities)) {
            capFilter.add(new Option(label, key));
        }
    }
    updateSubSelector();
    loadAll();
}

function updateSubSelector() {
  const benchmark = document.querySelector('input[name="benchmark"]:checked').value;
  const viewType = document.querySelector('input[name="viewType"]:checked').value;
  const subSelector = document.getElementById('subSelector');
  subSelector.innerHTML = '';

  let sourceData = {};
  if (benchmark === 'mmvet') {
      sourceData = (viewType === 'method') ? METHOD_SETS : GENERATOR_SETS;
  } else if (benchmark === 'cvbench') { // cvbench
      if (viewType === 'method') {
          sourceData = CVBENCH_CONFIG.methodSets;
      } else {
          sourceData = Object.fromEntries(
              Object.entries(CVBENCH_CONFIG.generators).map(([key, value]) => [key, value.label])
          );
      }
  } else if (benchmark === 'mmmu') {
    if (viewType === 'method') {
        sourceData = MMMU_CONFIG.methodSets;
    } else {
        sourceData = Object.fromEntries(
            Object.entries(MMMU_CONFIG.generators).map(([key, value]) => [key, value.label])
        );
    }
}

  for (const [key, label] of Object.entries(sourceData)) { subSelector.add(new Option(label, key)); }
}
async function loadAll() {
    showLoader(true);
    const benchmark = document.querySelector('input[name="benchmark"]:checked').value;
    
    if (benchmark === 'mmvet') {
        await loadAll_mmvet_original();
    } else if (benchmark === 'cvbench') {
        await loadAll_cvbench_new();
    } else if (benchmark === 'mmmu') {
        await loadAll_mmmu_new();
    }
    showLoader(false);
}
async function loadAll_cvbench_new() {
  console.time('loadAll_cvbench_new');
  const meta = {};
  const preds = {};
  const scores = {};

  const benchmark = document.querySelector('input[name="benchmark"]:checked').value;
  const viewType  = document.querySelector('input[name="viewType"]:checked').value;
  const subKey    = document.getElementById('subSelector').value;

  console.log('[CVB] benchmark=', benchmark, 'viewType=', viewType, 'subKey=', subKey);
  console.log('[CVB] variantsByMethod keys =', Object.keys(CVBENCH_CONFIG.renderConfig.variantsByMethod || {}));
  console.log('[CVB] variantsByMethod[subKey] =', (CVBENCH_CONFIG.renderConfig.variantsByMethod || {})[subKey]);
  console.log('[CVB] generator keys =', Object.keys(CVBENCH_CONFIG.generators || {}));

  const origConfig = CVBENCH_CONFIG.origConfig;
  preds['orig'] = {};
  scores['orig'] = {};
  try {
    const origFilePromises = (origConfig.files || []).map(
      file => fetchText(`${origConfig.name}/${file}`)
                .then(parseJSONL)
                .catch(e => { console.warn('[CVB] orig file fail:', file, e); return []; })
    );
    const allOrigData = (await Promise.all(origFilePromises)).flat();

    for (const item of allOrigData) {
      const uniqueId = `${item.source}-${item.questionId}`;
      if (!meta[uniqueId]) {
        meta[uniqueId] = {
          imagename: item.image,
          question: item.prompt,
          answer: item.gt_answer,
          capability: [item.category]
        };
      }
      preds['orig'][uniqueId] = item.answer ?? '';
      let score = 0.0;
      if (typeof item.answer === 'string') {
        const m = item.answer.match(/\([A-Z]\)/);
        if (m && item.gt_answer && m[0].toLowerCase() === item.gt_answer.trim().toLowerCase()) score = 1.0;
      }
      scores['orig'][uniqueId] = { score: [score] };
    }
    console.log('[CVB] loaded ORIG items =', Object.keys(preds['orig']).length);
  } catch (e) {
    console.error('[CVB] load orig failed:', e);
  }

  let generatorKeys = [];
  if (viewType === 'method') {
    generatorKeys = (CVBENCH_CONFIG.renderConfig.variantsByMethod[subKey] || []).slice();
  } else {
    generatorKeys = [subKey];
  }
  console.log('[CVB] generatorKeys =', generatorKeys);
  if (viewType === 'method' && generatorKeys.length === 0) {
    console.warn('[CVB] variantsByMethod[subKey] is empty !');
  }

  for (const key of generatorKeys) {
    const genConfig = CVBENCH_CONFIG.generators[key];
    if (!genConfig) {
      console.warn('[CVB] generator key skipped', key);
      continue;
    }

    const folderName = genConfig.name;
    preds[key]  = {};
    scores[key] = {};

    try {
      const filePromises = (genConfig.files || []).map(
        file => fetchText(`${folderName}/${file}`)
                  .then(parseJSONL)
                  .catch(e => { console.warn(`[CVB] ${key} file fail:`, `${folderName}/${file}`, e); return []; })
      );
      const allDataForModel = (await Promise.all(filePromises)).flat();

      for (const item of allDataForModel) {
        const uniqueId = `${item.source}-${item.questionId}`;
        if (!meta[uniqueId]) {
          meta[uniqueId] = {
            imagename: item.image,
            question: item.prompt,
            answer: item.gt_answer,
            capability: [item.category]
          };
        }
        preds[key][uniqueId] = item.answer ?? '';
        let score = 0.0;
        if (typeof item.answer === 'string') {
          const m = item.answer.match(/\([A-Z]\)/);
          if (m && item.gt_answer && m[0].toLowerCase() === item.gt_answer.trim().toLowerCase()) score = 1.0;
        }
        scores[key][uniqueId] = { score: [score] };
      }
      console.log(`[CVB] loaded ${key}:`, Object.keys(preds[key]).length, 'items');
    } catch (e) {
      console.error(`[CVB] load ${key} failed:`, e);
    }
  }

  render(meta, preds, scores, {});
  console.timeEnd('loadAll_cvbench_new');
}
async function loadAll_mmmu_new() {
    const meta = {};
    const preds = {};
    const scores = {};
    const allQuestions = await fetchJSON(MMMU_CONFIG.questionFile);
    for (const q of allQuestions) {
        const subtask = q.id.split('_').slice(1, -1).join('_');
        meta[q.id] = { imagename: '', question: q.prompt, answer: '', capability: [subtask] };
    }

    const origConfig = MMMU_CONFIG.origConfig;
    preds['orig'] = {};
    scores['orig'] = {};
    const origFilePromises = MMMU_CONFIG.subtasks.map(subtask => 
        fetchJSON(`${origConfig.name}/predictions/${subtask}/parsed_output.json`)
    );
    const allOrigData = (await Promise.all(origFilePromises)).flat();

    for (const item of allOrigData) {
        if (!meta[item.id]) continue;
        if (!meta[item.id].answer) { meta[item.id].answer = item.answer; }
        preds['orig'][item.id] = item.response;
        scores['orig'][item.id] = { score: [(item.judge === 'Correct') ? 1.0 : 0.0] };
    }

    const viewType = document.querySelector('input[name="viewType"]:checked').value;
    const subKey = document.getElementById('subSelector').value;
    
    let generatorKeys = (viewType === 'method')
        ? MMMU_CONFIG.renderConfig.variantsByMethod[subKey] || []
        : [subKey];
    
    for (const key of generatorKeys) {
        const genConfig = MMMU_CONFIG.generators[key];
        if (!genConfig) continue;
        preds[key] = {};
        scores[key] = {};
        const filePromises = MMMU_CONFIG.subtasks.map(subtask => 
            fetchJSON(`${genConfig.name}/predictions/${subtask}/parsed_output.json`)
        );
        const allDataForModel = (await Promise.all(filePromises)).flat();
        for (const item of allDataForModel) {
            if (!meta[item.id]) continue;
            if (!meta[item.id].answer) { meta[item.id].answer = item.answer; }
            preds[key][item.id] = item.response;
            scores[key][item.id] = { score: [(item.judge === 'Correct') ? 1.0 : 0.0] };
        }
    }
    render(meta, preds, scores, {});
}
async function loadAll_mmvet_original(){
  const tag  = document.getElementById('modelSel').value;
  const meta = await fetchJSON(DATA_JSON);
  const preds  = {}, scores = {}, texts = {};
  await Promise.all(Object.entries(PRED_SET[tag]).map(async([k,p])=> preds[k]  = await fetchJSON(p)));
  await Promise.all(Object.entries(SCORE_SET[tag]).map(async([k,p])=> scores[k] = await fetchJSON(p)));
  const textPromises = Object.entries(TEXT_SET).map(async ([key, path]) => {
      texts[key] = await fetchJSON(path);
  });
  await Promise.all(textPromises);
  
  render(meta, preds, scores, texts);
}
function render(meta, preds, scores, texts){
  const benchmark = document.querySelector('input[name="benchmark"]:checked').value;

  const thead = document.querySelector('table thead');
  const tbody = document.getElementById('dataBody');
  const viewType = document.querySelector('input[name="viewType"]:checked').value;
  const subKey = document.getElementById('subSelector').value;
  tbody.innerHTML='';
  let idx=0;

  const currentRenderConfig = 
      (benchmark === 'mmvet') ? renderConfig : 
      (benchmark === 'cvbench') ? CVBENCH_CONFIG.renderConfig : 
      MMMU_CONFIG.renderConfig;

  const currentGeneratorVariants = (benchmark === 'mmvet') ? GENERATOR_VARIANTS : null;
  const {variantsByMethod, headerLabels, scoreLabels} = currentRenderConfig;
  
  let syntheticTypes = [];

  if (viewType === 'method') { 
      syntheticTypes = variantsByMethod[subKey] || []; 
  } else if (viewType === 'gen') { 
      syntheticTypes = (benchmark === 'mmvet' && currentGeneratorVariants) ? currentGeneratorVariants[subKey] || [] : [subKey];
  }

  
  const availableSynthTypes = syntheticTypes.filter(type => preds[type]);
  const imageTypes = ['orig'].concat(availableSynthTypes);
  
  let headerHTML = '<tr>';
  const thClasses = 'sticky top-0 z-10 bg-gray-50 border-b border-gray-200 px-3 py-3 text-left text-sm font-medium text-gray-600';
  headerHTML += `<th class="${thClasses}">#</th>`;
  imageTypes.forEach(key => headerHTML += `<th class="${thClasses}">${headerLabels[key] || key}</th>`);
  headerHTML += `<th class="${thClasses}">Question</th><th class="${thClasses}">Answer</th><th class="${thClasses}">Caps</th>`;
  headerHTML += '</tr>';
  thead.innerHTML = headerHTML;

  for(const [id,d] of Object.entries(meta)){
    const tr = document.createElement('tr');
    tr.dataset.cls = d.capability.join(',');
    tr.className = 'hover:bg-gray-50 transition-colors duration-150';
    const idxCell = document.createElement('td');
    idxCell.className = 'px-3 py-3 text-center text-gray-500';
    idxCell.textContent = ++idx;
    tr.appendChild(idxCell);
    
    imageTypes.forEach(key=> {
        const textContent = texts[key] ? texts[key][id] : null;
        let imagePath = '';
        if (benchmark === 'mmvet') {
            imagePath = IMG_DIR[key] + d.imagename;
        } else if (benchmark === 'cvbench') {
            const isOrig = key === 'orig';
            const folderName = isOrig ? CVBENCH_CONFIG.origConfig.name : CVBENCH_CONFIG.generators[key]?.name;
            
            if (folderName) {
                let finalImageName = d.imagename;
                imagePath = `${folderName}/${finalImageName}`;
            }
        } else if (benchmark === 'mmmu') {
          const isOrig = key === 'orig';
          const folderName = isOrig ? MMMU_CONFIG.origConfig.name : MMMU_CONFIG.generators[key]?.name;
      
          if (folderName) {
              imagePath = `${folderName}/${getMmmuImagePath(id)}`;
          }
        }
        
        const scoreData = scores[key]?.[id]?.score?.[0];
        const predData = preds[key]?.[id];
        tr.appendChild(imgCell(imagePath, scoreData, predData, textContent));
    });

    tr.appendChild(clipCell(d.question,'Question'));
    tr.appendChild(clipCell(d.answer,'Answer'));
    const capsCell = document.createElement('td');
    capsCell.className = 'px-3 py-3 text-gray-700';
    capsCell.textContent = d.capability.join(', ');
    tr.appendChild(capsCell);
    tbody.appendChild(tr);
  }
  filterRows();
  showLoader(false);
}
function filterRows(){
  document.querySelector('#noResultsRow')?.remove();
  const tbody = document.getElementById('dataBody');
  const cap = document.getElementById('capabilityFilter').value;
  const kw  = document.getElementById('searchInput').value.toLowerCase();
  let visibleCount = 0;
  
  tbody.querySelectorAll('tr').forEach(tr=>{
    const okCap = cap==='all' || tr.dataset.cls.includes(cap);
    const okKw  = tr.innerText.toLowerCase().includes(kw);
    if(okCap && okKw) {
        tr.style.display = '';
        visibleCount++;
    } else {
        tr.style.display = 'none';
    }
  });

  if (visibleCount === 0 && tbody.innerHTML !== '') {
    const cols = document.querySelector('table thead tr').cells.length;
    const noResultsRow = tbody.insertRow();
    noResultsRow.id = 'noResultsRow';
    const cell = noResultsRow.insertCell();
    cell.colSpan = cols;
    cell.className = 'text-center text-gray-500 py-12';
    cell.textContent = 'No results found.';
  }
}
document.querySelectorAll('input[name="benchmark"]').forEach(radio => radio.addEventListener('change', handleBenchmarkSwitch));
document.querySelectorAll('input[name="viewType"]').forEach(radio => { radio.addEventListener('change', () => { updateSubSelector(); loadAll(); }); });
document.getElementById('subSelector').addEventListener('change', loadAll);
document.getElementById('modelSel').addEventListener('change', loadAll);
document.getElementById('searchInput').addEventListener('input', filterRows);
document.getElementById('capabilityFilter').addEventListener('change', filterRows);

handleBenchmarkSwitch();