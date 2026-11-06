const translations=JSON.parse(document.getElementById('workspace-translations').textContent);
const claims=JSON.parse(document.getElementById('workspace-data').textContent);
const names={tid:'Readout ID',name:'Readout name',type:'Value type code',unit:'Unit code'};
const hints={tid:'Exact readout identifier in the source schema.',name:'Readout name as declared by the provider.',type:'Raw value-type code retained.',unit:'Raw unit code retained; no conversion.'};
let selectedIndex=Math.max(0,claims.findIndex(c=>c.key==='name'&&c.state==='VALUE'));
let language='en';
const text=key=>language==='th'&&translations[key]?translations[key]:key;
function selectField(index,focus=false){
  if(!Number.isInteger(index)||index<0||index>=claims.length)return;
  selectedIndex=index;const claim=claims[index];
  document.getElementById('selected-field-name').textContent=text(names[claim.key]||claim.key);
  const value=document.getElementById('selected-field-value');
  const structured=claim.state==='VALUE'&&claim.value!==null&&typeof claim.value==='object';
  value.textContent=claim.state==='VALUE'?(typeof claim.value==='string'?claim.value:JSON.stringify(claim.value,null,structured?2:0)):'—';
  value.dataset.type=structured?'structured':value.textContent.length>64?'long':'scalar';
  value.dataset.field=claim.key;
  document.getElementById('selected-field-description').textContent=text(hints[claim.key]||'Original provider metadata.');
  if(structured)value.setAttribute('tabindex','0');else value.removeAttribute('tabindex');
  document.getElementById('trail-key').textContent=claim.key;
  document.getElementById('trail-source').textContent=claim.evidence.source_id;
  document.getElementById('selected-locator').textContent=claim.evidence.locator;
  document.querySelectorAll('[data-select-index]').forEach(button=>{
    const active=Number(button.dataset.selectIndex)===index;
    button.setAttribute('aria-pressed',String(active));
    button.closest('tr').dataset.selected=String(active);
    if(active&&focus)button.focus();
  });
  document.querySelectorAll('[data-source-id]').forEach(source=>{source.hidden=source.dataset.sourceId!==claim.evidence.source_id});
}
function setLanguage(lang){
  language=lang;document.documentElement.lang=lang;
  document.querySelectorAll('[data-i18n]').forEach(el=>{el.textContent=text(el.dataset.i18n)});
  document.querySelectorAll('[data-language]').forEach(el=>el.setAttribute('aria-pressed',String(el.dataset.language===lang)));
  document.querySelector('.language').setAttribute('aria-label',lang==='th'?'ภาษา':'Language');
  document.querySelector('nav').setAttribute('aria-label',lang==='th'?'พื้นที่ทำงาน':'Workspace');
  document.querySelector('.table-wrap').setAttribute('aria-label',text('Declared fields'));
  document.getElementById('mobile-nav-toggle').setAttribute('aria-label',text('Open navigation'));
  selectField(selectedIndex);
  try{localStorage.setItem('curaloop-language',lang)}catch{}
}
document.querySelectorAll('[data-language]').forEach(button=>button.addEventListener('click',()=>setLanguage(button.dataset.language)));
const menu=document.getElementById('mobile-nav-toggle');
const navigation=document.getElementById('workspace-nav');
function closeMenu(){navigation.dataset.open='false';menu.setAttribute('aria-expanded','false')}
menu.addEventListener('click',()=>{const open=navigation.dataset.open!=='true';navigation.dataset.open=String(open);menu.setAttribute('aria-expanded',String(open))});
document.addEventListener('keydown',event=>{if(event.key==='Escape'&&navigation.dataset.open==='true'){closeMenu();menu.focus()}});
navigation.querySelectorAll('a').forEach(link=>link.addEventListener('click',()=>{navigation.querySelectorAll('a').forEach(item=>item.classList.toggle('active',item===link));closeMenu()}));
document.querySelectorAll('[data-select-index]').forEach(button=>{
  button.addEventListener('click',()=>selectField(Number(button.dataset.selectIndex)));
  button.addEventListener('keydown',event=>{
    if(event.key==='ArrowDown'||event.key==='ArrowUp'){
      event.preventDefault();selectField((Number(button.dataset.selectIndex)+(event.key==='ArrowDown'?1:-1)+claims.length)%claims.length,true);
    }
  });
});
let initial='en';try{if(localStorage.getItem('curaloop-language')==='th')initial='th'}catch{}
setLanguage(initial);
