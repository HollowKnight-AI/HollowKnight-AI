'use strict';
const look=document.documentElement.dataset.homeLook;
const query=new URLSearchParams(location.search);
// Explicit links select a view; a direct visit to the default home remembers
// the visitor's last view. Changing views never changes the public data.
try{
  if(look==='vcard'&&!query.has('style')&&localStorage.getItem('public-home-look')==='github'){
    location.replace('github.html?style=github'+location.hash);
  }else localStorage.setItem('public-home-look',look);
}catch{/* Browsers that disable storage still support both direct URLs. */}
document.querySelectorAll('[data-look-link]').forEach(link=>link.addEventListener('click',()=>{
  const section=document.querySelector('[data-page].active')?.dataset.section||location.hash.slice(1);
  const key=look==='vcard'?({about:'',resume:'projects',portfolio:'projects',blog:'posts'}[section]||''):({projects:'portfolio',interests:'about',posts:'blog'}[section]||'about');
  if(key)link.hash=key;
}));
let documents=[],ready=false,failed=false;
const search=document.getElementById('home-search'),results=document.getElementById('home-results');
const make=(tag,text)=>{const el=document.createElement(tag);el.textContent=text;return el;};
function runSearch(){
  results.replaceChildren();const tokens=search.value.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);if(!tokens.length)return;
  if(!ready){results.append(make('p',failed?'搜索暂不可用，请使用页面导航。':'正在读取公开索引…'));return;}
  const rows=documents.filter(row=>tokens.every(t=>(row.title+' '+row.text).toLocaleLowerCase().includes(t))).slice(0,10);
  if(!rows.length)results.append(make('p','没有找到匹配的公开记录。'));
  for(const row of rows){const a=make('a',row.title);a.href=row.source==='README.md'?'notebook.html':row.path;a.append(make('small',row.text.slice(0,110)+'…'));results.append(a);}
}
search.addEventListener('input',runSearch);
fetch('search.json',{cache:'no-cache'}).then(r=>{if(!r.ok)throw Error();return r.json();}).then(data=>{documents=data;ready=true;runSearch();}).catch(()=>{failed=true;runSearch();});
if(look==='vcard'){
  const nav=[...document.querySelectorAll('[data-nav-link]')],pages=[...document.querySelectorAll('[data-page]')];
  function restoreSection(){const key=location.hash.slice(1)||'about';const button=nav.find(b=>b.dataset.section===key);if(button)button.click();}
  nav.forEach(b=>b.addEventListener('click',()=>{nav.forEach(n=>n.setAttribute('aria-pressed',String(n===b)));history.replaceState(null,'','#'+b.dataset.section);}));
  window.addEventListener('hashchange',restoreSection);restoreSection();
  const sidebar=document.querySelector('[data-sidebar]'),sidebarButton=document.querySelector('[data-sidebar-btn]');
  sidebarButton.addEventListener('click',()=>sidebarButton.setAttribute('aria-expanded',String(sidebar.classList.contains('active'))));
  const select=document.querySelector('[data-select]');select.addEventListener('click',()=>select.setAttribute('aria-expanded',String(select.classList.contains('active'))));
  const categories=[...document.querySelectorAll('[data-filter-btn]')];
  function syncCategory(label){categories.forEach(b=>{const active=b.textContent.trim()===label;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});select.setAttribute('aria-expanded','false');}
  document.querySelectorAll('[data-filter-btn],[data-select-item]').forEach(b=>b.addEventListener('click',()=>syncCategory(b.textContent.trim())));
  syncCategory('全部');
}
