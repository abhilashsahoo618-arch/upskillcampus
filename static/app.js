const form=document.getElementById('verify-form');
const statusBox=document.getElementById('status');
const resultSection=document.getElementById('result-section');
const eventsSection=document.getElementById('events-section');

function status(message,error=false){statusBox.textContent=message;statusBox.classList.remove('hidden','error');if(error)statusBox.classList.add('error')}
function clearStatus(){statusBox.classList.add('hidden');statusBox.textContent=''}
function list(el,items,empty){el.innerHTML='';if(!items||!items.length){const li=document.createElement('li');li.textContent=empty;el.appendChild(li);return}items.forEach(x=>{const li=document.createElement('li');li.textContent=x;el.appendChild(li)})}
function card(title,meta,url,body=''){const d=document.createElement('div');d.className='evidence-item';const h=document.createElement('strong');h.textContent=title||'Untitled';d.appendChild(h);if(meta){const p=document.createElement('p');p.textContent=meta;d.appendChild(p)}if(body){const p=document.createElement('p');p.textContent=body;d.appendChild(p)}if(url){const a=document.createElement('a');a.href=url;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Open source';d.appendChild(a)}return d}

form.addEventListener('submit',async e=>{
  e.preventDefault();resultSection.classList.add('hidden');status('Analyzing. Videos may take longer...');
  try{
    const r=await fetch('/api/analyze',{method:'POST',body:new FormData(form)});const data=await r.json();if(!r.ok)throw new Error(data.error||'Analysis failed');clearStatus();
    document.getElementById('verdict').textContent=data.verdict;document.getElementById('confidence-badge').textContent=`Confidence: ${data.confidence}`;
    const score=Number(data.heuristic_score||0);document.getElementById('score-value').textContent=`${score}/100`;document.getElementById('score-fill').style.width=`${score}%`;
    list(document.getElementById('positive-list'),data.positive_signals,'No strong positive signals detected.');list(document.getElementById('red-list'),data.red_flags,'No obvious wording red flags detected.');
    const box=document.getElementById('extracted-box');if(data.extracted_text){document.getElementById('extracted-text').textContent=data.extracted_text;box.classList.remove('hidden')}else box.classList.add('hidden');
    const facts=document.getElementById('fact-checks');facts.innerHTML='';if(data.fact_checks?.length){data.fact_checks.forEach(x=>facts.appendChild(card(x.claim||'Fact-check match',`${x.publisher||'Fact checker'} • Rating: ${x.rating||'Unknown'}`,x.url,x.claimant?`Claimant: ${x.claimant}`:'')))}else facts.textContent='No configured fact-check match was found.';
    const news=document.getElementById('news-matches');news.innerHTML='';if(data.news_matches?.length){data.news_matches.forEach(x=>news.appendChild(card(x.title,`${x.source||'News source'} • ${x.published_at||''}`,x.url,x.description||'')))}else news.textContent='No related live news results were returned.';
    document.getElementById('explanation').textContent=data.explanation;resultSection.classList.remove('hidden');resultSection.scrollIntoView({behavior:'smooth'})
  }catch(err){status(err.message,true)}
});

document.getElementById('clear-btn').addEventListener('click',()=>{form.reset();resultSection.classList.add('hidden');clearStatus()});

document.getElementById('load-events-btn').addEventListener('click',async()=>{
  eventsSection.classList.remove('hidden');const grid=document.getElementById('events-grid');const warning=document.getElementById('events-warning');grid.innerHTML='';warning.classList.add('hidden');
  try{const r=await fetch('/api/events?country=in&category=general');const data=await r.json();if(data.warning){warning.textContent=data.warning;warning.classList.remove('hidden')}if(!data.events?.length)return;data.events.forEach(x=>{const d=card(x.title,`${x.source||'Unknown source'} • ${x.published_at||''}`,x.url,x.description||'');d.className='event-card';grid.appendChild(d)});eventsSection.scrollIntoView({behavior:'smooth'})}catch(err){warning.textContent=err.message;warning.classList.remove('hidden')}
});
