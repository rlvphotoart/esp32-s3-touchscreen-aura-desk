#!/usr/bin/env python3
"""Run offline DOM regressions against the exact embedded browser JavaScript.

This is a host logic check, separate from Safari/device verification. It uses
public example constants and synthetic status bodies; no real network, device,
pairing codes or saved settings are accessed or output. Generated scripts are
private temporary files removed on completion.
"""
import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HARNESS = r'''
const fs=require('fs'),vm=require('vm');
let assertions=0;
function check(condition,name){assertions++;if(!condition)throw Error('FAIL: '+name)}
class Element {
  constructor(id){this.id=id;this.textContent='';this._value='';this.checked=false;this.disabled=false;this.className='';this.type='';this.files=[];this.button={disabled:false};this.children=[];this.dataset={};
    this.classList={add:(...names)=>{const current=new Set(this.className.split(/\s+/).filter(Boolean));names.forEach(n=>current.add(n));this.className=[...current].join(' ')},remove:(...names)=>{this.className=this.className.split(/\s+/).filter(n=>n&&!names.includes(n)).join(' ')},contains:name=>this.className.split(/\s+/).includes(name)};
  }
  get value(){return this._value}
  set value(value){const proposed=String(value);if(/^widget(service|example)[01]$/.test(this.id)){const options=this.children.flatMap(child=>child.id==='option'?[child]:child.children);this._value=options.some(option=>option.value===proposed)?proposed:''}else this._value=proposed}
  querySelector(selector){if(selector==='button')return this.button;throw Error('Unknown DOM selector in offline harness')}
  querySelectorAll(selector){if(selector==='button')return /^widget[01]$/.test(this.id)?[node('widgetuse'+this.id.slice(-1)),node('widgetsavetop'+this.id.slice(-1)),this.button]:[this.button];throw Error('Unknown DOM selector in offline harness')}
  appendChild(node){this.children.push(node);return node}
  replaceChildren(...nodes){this.children=[...nodes]}
  removeAttribute(name){delete this[name]}
  focus(){focusedId=this.id}
  scrollIntoView(){scrolledId=this.id}
  click(){}
}
const nodes=new Map();
const node=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id)};
let focusedId='',scrolledId='';
let requests=[],reply=async()=>({status:401,ok:false,json:async()=>({error:'Pair again.'})});
let nextTimer=1;const timers=new Map(),intervals=[];
const context={document:{getElementById:node,createElement:tag=>new Element(tag)},fetch:async(path,options)=>{requests.push({path,options});return reply(path,options)},AbortController,TextEncoder,setInterval:callback=>{intervals.push(callback);return intervals.length},setTimeout:(callback,delay)=>{const id=nextTimer++;timers.set(id,{callback,delay});return id},clearTimeout:id=>timers.delete(id),Blob:class {},URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}},XMLHttpRequest:class {}};
vm.createContext(context);
const evaluate=source=>vm.runInContext(source,context,{filename:'AURA embedded browser checks'});
const clone=value=>JSON.parse(JSON.stringify(value));
function status(){return {csrf:'offline-test-placeholder',city:'Example city',connection:'Online',latitude:12.34567,longitude:-45.67891,clock:'00:00',date:'Example date',ssid:'',ip:'192.0.2.1',firmware:'AURA Desk host fixture',resetReason:'Host fixture',uptimeSeconds:1,freeHeap:100000,minimumHeap:90000,psramBytes:8388608,rssi:0,brightness:80,alwaysOnDisplay:true,wifiConnected:true,timeSynced:true,weatherValid:false,airValid:false,ratesValid:false,widgets:[{enabled:true,valid:true,value:'0',unit:'%',ageMinutes:0,error:'',fetching:false},{enabled:false,valid:false,value:'',unit:'',ageMinutes:-1,error:'',fetching:false}],widgetConfig:[{label:'Original one',url:'https://example.org/one.json',field:'data.0.price',unit:'USD',interval:300,enabled:true},{label:'Original two',url:'',field:'',unit:'',interval:1800,enabled:false}]}}
function renderWidget(widget,state=status()){context.fixture=widget;context.fixtureStatus=state;evaluate('showWidget(0,fixture,fixtureStatus)')}
async function main(){
  evaluate(fs.readFileSync(process.argv[2],'utf8'));
  await new Promise(resolve=>setImmediate(resolve));
  const initialRequests=requests.length;
  await evaluate('poll()');await intervals[0]();
  check(requests.length===initialRequests,'Unpaired session performs one initial status check and stops polling');
  requests=[];reply=async()=>({status:401,ok:false,json:async()=>({error:'The code does not match. Check the device.'})});
  node('code').value='000000';await node('pairform').onsubmit({preventDefault(){}});
  const wrongPairFeedback=node('pairformfeedback').textContent,requestsAfterWrongPair=requests.length;
  await evaluate('poll()');await intervals[0]();
  check(wrongPairFeedback.includes('does not match')&&node('pairformfeedback').textContent===wrongPairFeedback,'Wrong pairing-code feedback survives subsequent polling ticks');
  check(requests.length===requestsAfterWrongPair&&!node('pairform').button.disabled,'Wrong Pair does not trigger more status requests or leave its button disabled');
  context.fixtureStatus=status();evaluate('showStatus(fixtureStatus)');
  check(node('widgetvalue0').textContent==='0 %','Zero is displayed as a valid scalar');
  check(node('widgetstate0').textContent.includes('last request succeeded'),'Successful state is clear');
  check(node('widgetvalue1').textContent==='Disabled','Disabled second widget is distinct');

  renderWidget({enabled:true,valid:true,value:false,unit:'',ageMinutes:0,error:'',fetching:false});
  check(node('widgetvalue0').textContent==='false','False does not disappear through truthiness coercion');
  renderWidget({enabled:true,valid:true,value:'42',unit:'%',ageMinutes:7,error:'Endpoint unavailable.',httpStatus:404,fetching:false});
  check(node('widgetvalue0').textContent==='42 %','Failed update retains the last successful reading');
  check(node('widgetstate0').classList.contains('bad')&&node('widgetstate0').textContent.includes('404'),'Per-widget error is visible');
  check(node('widgetage0').textContent.includes('Last successful reading')&&node('widgetage0').textContent.includes('7 min'),'Retained reading keeps its age and stale context');
  renderWidget({enabled:true,valid:false,value:'',unit:'',ageMinutes:-1,error:'JSON field was not found.',httpStatus:200,fetching:false});
  check(node('widgetvalue0').textContent==='—'&&node('widgetstate0').textContent.includes('not found'),'First-request missing field has an actionable error');
  check(!node('widgetstate0').textContent.includes('HTTP 200'),'Successful HTTP code does not obscure a JSON field error');
  renderWidget({enabled:true,valid:false,error:'',fetching:true});
  check(node('widgetstate0').textContent.includes('Fetching'),'Fetch in progress is visible');
  let offline=status();offline.wifiConnected=false;renderWidget({enabled:true,valid:false,error:'',fetching:false},offline);
  check(node('widgetstate0').textContent.includes('Wi-Fi'),'Wi-Fi prerequisite is shown');
  offline=status();offline.timeSynced=false;renderWidget({enabled:true,valid:false,error:'',fetching:false},offline);
  check(node('widgetstate0').textContent.includes('clock'),'Clock prerequisite is shown');

  for(const example of ['bitcoin','humidity','eurRon','carbon']){
    context.example=example;evaluate('applyExample(0,example)');
    check(node('widgeturl0').value.startsWith('https://'),'Examples use HTTPS');
    check(!/api[_-]?key|token=|password=|\/\/[^/]*@/i.test(node('widgeturl0').value),'Examples require no keys or embedded credentials');
    check(node('widgetenabled0').checked===true&&Number(node('widgetinterval0').value)>=300,'Examples produce enabled configuration and supported interval');
    check(node('widget0feedback').textContent.includes('save'),'Selecting an example asks the user to save without dispatching it');
    if(example==='bitcoin')check(node('widgetfield0').value==='data.amount','Public Coinbase spot example selects the amount scalar');
    if(example==='carbon')check(node('widgetfield0').value==='data.0.intensity.forecast','Carbon example selects array item zero');
    if(example==='eurRon')check(node('widgetfield0').value==='rates.RON','Currency example selects the named rate');
    if(example==='humidity')check(node('widgeturl0').value.includes('latitude=12.3457')&&node('widgeturl0').value.includes('longitude=-45.6789'),'City example uses current saved coordinates');
  }
  const selectOptions=id=>node(id).children.flatMap(child=>child.id==='option'?[child]:child.children);
  const options=i=>node('widgetexample'+i).children.flatMap(child=>child.id==='option'?[child]:child.children);
  const originalIds=evaluate('Object.keys(WIDGET_EXAMPLES)'),ids=evaluate('Object.keys(WIDGET_READINGS)'),services=evaluate('API_SERVICES');
  check(originalIds.length===100,'Original runtime retains exactly100 preset choices');
  check(services.length===500,'Runtime contains exactly500 distinct API services');
  check(new Set(services.map(service=>service.id)).size===500,'Every service has a distinct selectable ID');
  check(ids.length>=100,'Merged runtime preserves every original preset');
  for(let i=0;i<2;i++){
    node('widgetservice'+i).value='';node('widgetservice'+i).onchange();
    check(options(i).filter(option=>option.value).length===ids.length,'Each reading dropdown contains the complete merged presets');
    check(selectOptions('widgetservice'+i).filter(option=>option.value).length===500,'Each service dropdown contains all500 choices');
    check(node('widgetexample'+i).children.some(child=>child.id==='optgroup'),'Catalog is grouped by topic in both slots');
    check(node('widgetcataloginfo'+i).textContent.startsWith('500 services'),'Visible service count agrees with actual options');
    const requestsBefore=requests.length;
    for(const id of ids){
      context.catalogId=id;context.catalogSlot=i;
      const expected=evaluate('resolvedExample(catalogId)');
      evaluate('renderServices(catalogSlot,READING_SERVICE_INDEX.get(catalogId)||"");browseService(catalogSlot)');
      node('widgetexample'+i).value=id;node('widgetexample'+i).onchange();
      for(const key of ['label','url','field','unit','interval'])check(String(node('widget'+key+i).value)===String(expected[key]),'Each catalog choice fills its own saved-field mapping');
      check(node('widgetenabled'+i).checked===true,'Every catalog choice enables only its chosen widget');
      check(node('widgetdocs'+i).href===expected.docs&&!node('widgetdocs'+i).classList.contains('hide'),'Each choice exposes its verified provider documentation');
    }
    check(requests.length===requestsBefore,'Browsing all reading templates never dispatches an API request or save');
    const selected=node('widgetexample'+i).value,label=node('widgetlabel'+i).value,url=node('widgeturl'+i).value;
    node('widgetsearch'+i).value='NoAa';node('widgetsearch'+i).oninput();
    const noaaCount=evaluate('API_SERVICES.filter(entry=>serviceMatches(entry,"noaa")).length');
    check(noaaCount>0&&node('widgetcataloginfo'+i).textContent.startsWith(noaaCount+' matches'),'Search is case-insensitive across provider names');
    check(node('widgetexample'+i).value===selected&&node('widgetlabel'+i).value===label&&node('widgeturl'+i).value===url,'Search preserves selected preset and current form fields');
    node('widgetsearch'+i).value='no-such-api-fixture';node('widgetsearch'+i).oninput();
    check(node('widgetcataloginfo'+i).textContent.startsWith('0 matches'),'An empty result set has explicit feedback');
    check(options(i).some(option=>option.value===selected),'A selected choice remains reachable when filtered out');
    let prevented=false;node('widgetsearch'+i).onkeydown({key:'Enter',preventDefault(){prevented=true}});
    check(prevented&&requests.length===requestsBefore,'Enter in search cannot accidentally submit the configuration');
    node('widgetsearch'+i).value='';node('widgetsearch'+i).oninput();
    check(selectOptions('widgetservice'+i).filter(option=>option.value).length===500,'Clearing search restores all500 services without duplicates');
    node('widgetservice'+i).value='';node('widgetservice'+i).onchange();
    check(options(i).filter(option=>option.value).length===ids.length,'All services view restores every reading template');
  }
  for(let i=0;i<2;i++){
    node('widgetexample'+i).value='';node('widgetsearch'+i).value='';node('widgetsearch'+i).oninput();
    for(const key of ['label','url','field','unit','interval'])node('widget'+key+i).value=key==='url'?'https://example.org/draft.json':'draft-'+key;
    node('widgetenabled'+i).checked=false;
    const draft=Object.fromEntries(['label','url','field','unit','interval'].map(key=>[key,node('widget'+key+i).value])),before=requests.length;
    for(const service of services){
      node('widgetservice'+i).value=service.id;node('widgetservice'+i).onchange();
      check(node('widgetservice'+i).value===service.id,'All500 service options remain selectable');
      check(node('widgetservicename'+i).textContent===service.name&&!node('widgetprofile'+i).classList.contains('hide'),'Selected service profile is visible by its own name');
      check(node('widgetservicedocs'+i).href===service.docs_url,'Service details point to provider documentation');
      check(node('widgetserviceprovider'+i).textContent===service.provider,'Provider metadata matches selected service');
      check(node('widgetserviceaccess'+i).textContent.includes(service.auth)&&node('widgetserviceaccess'+i).textContent.includes(service.access),'Authentication and access limitations are visible');
      check(node('widgetserviceformats'+i).textContent===service.formats&&node('widgetservicefit'+i).textContent===service.current_firmware_fit,'Format and current device support remain explicit');
      const evidenceText=service.evidence_code==='provider_docs_reviewed'?'Provider documentation reviewed. Access requirements are shown above; each chosen endpoint still needs testing on the device.':service.evidence_code==='directory_only'?'Directory discovery. Confirm current access and endpoint behavior with the provider before configuring a widget.':service.evidence_status;
      check(node('widgetserviceevidence'+i).textContent===evidenceText,'Provider review versus directory discovery uses human-readable evidence without implying verified authentication');
      for(const key of Object.keys(draft))check(node('widget'+key+i).value===draft[key],'Service browsing preserves each draft field');
      check(node('widgetenabled'+i).checked===false,'Service browsing does not enable a widget');
      const readings=(service.reading_ids||[]).filter(id=>ids.includes(id));
      check(options(i).filter(option=>option.value).length===readings.length,'Selected service offers exactly its installed reading templates');
      if(!readings.length&&service.auth_code!=='requires_key'&&service.fit_code!=='adapter')check(node('widgetservicehint'+i).textContent.includes('No reading template'),'A supported service without readings explains manual endpoint setup');
    }
    check(requests.length===before,'Browsing every service in either slot never sends provider requests or configuration saves');
    const selected=node('widgetservice'+i).value;
    node('widgetsearch'+i).value='no-such-api-fixture';node('widgetsearch'+i).oninput();
    check(node('widgetservice'+i).value===selected&&selectOptions('widgetservice'+i).some(option=>option.value===selected),'Filtering retains the selected service outside the result set');
    node('widgetsearch'+i).value='';node('widgetsearch'+i).oninput();
    check(selectOptions('widgetservice'+i).filter(option=>option.value).length===500,'Full500 service list returns after search is cleared');
    node('widgetservice'+i).value='';node('widgetservice'+i).onchange();
    check(node('widgetprofile'+i).classList.contains('hide')&&!node('widgetservicedocs'+i).href,'Clearing service hides outdated metadata and documentation link');
  }
  // Browsing is intentionally read-only. The explicit Use action must turn each
  // catalog entry into either a real reading draft or a clean manual draft.
  for(let i=0;i<2;i++){
    const before=requests.length,other=i===0?1:0;
    const otherDraft=Object.fromEntries(['label','url','field','unit','interval'].map(key=>[key,node('widget'+key+other).value]));
    check(node('widgetuse'+i).disabled,'Use API is disabled when no service is selected');
    for(const service of services){
      node('widgetservice'+i).value=service.id;node('widgetservice'+i).onchange();
      const readings=(service.reading_ids||[]).filter(id=>ids.includes(id));
      node('widgetexample'+i).value='';
      if(!readings.length&&(service.auth_code==='requires_key'||service.fit_code==='adapter')){
        const priorDraft=Object.fromEntries(['label','url','field','unit','interval'].map(key=>[key,node('widget'+key+i).value]));
        check(node('widgetuse'+i).disabled,'Unsupported credential or adapter service has no misleading Use API action');
        node('widgetuse'+i).onclick();
        for(const key of Object.keys(priorDraft))check(node('widget'+key+i).value===priorDraft[key],'Unsupported service action cannot overwrite the current draft');
        check(/key|credential|support|format/i.test(node('widgetservicehint'+i).textContent),'Unsupported service shows its access or format limitation');
        continue;
      }
      check(!node('widgetuse'+i).disabled,'Every selected service has an explicit Use API action');
      node('widgetuse'+i).onclick();
      context.catalogSlot=i;
      check(evaluate('WIDGET_DRAFT_SERVICE[catalogSlot]')===service.id,'Using a service associates that service with its draft');
      check(node('widgetenabled'+i).checked===true,'Using a service prepares an enabled custom widget');
      if(readings.length){
        context.catalogId=readings[0];const expected=evaluate('resolvedExample(catalogId)');
        check(node('widgetexample'+i).value===readings[0],'Use API chooses the first installed reading when none is selected');
        for(const key of ['label','url','field','unit','interval'])check(String(node('widget'+key+i).value)===String(expected[key]),'Use API fills the actual reading endpoint and field mapping');
      }else{
        const label=node('widgetlabel'+i).value;
        check(Boolean(label)&&Buffer.byteLength(label,'utf8')<=27&&service.name.startsWith(label),'Manual service draft has a nonempty provider label within the firmware byte limit');
        check(node('widgeturl'+i).value===''&&node('widgetfield'+i).value===''&&node('widgetunit'+i).value==='','A service without a reading clears unrelated endpoint, field and unit');
        check(node('widgetexample'+i).value===''&&node('widgetinterval'+i).value==='1800','Manual service draft clears the old reading and uses a supported refresh interval');
        check(node('widgetservicedocs'+i).href===service.docs_url,'Manual service retains documentation solely as its provider link');
        check(focusedId==='widgeturl'+i,'Manual service setup puts focus on the required endpoint');
      }
      for(const key of Object.keys(otherDraft))check(node('widget'+key+other).value===otherDraft[key],'Use API does not change the other custom widget');
    }
    check(requests.length===before,'Actions across all500 services never POST saves or contact providers');
    const multiReadingService=services.find(service=>(service.reading_ids||[]).filter(id=>ids.includes(id)).length>1);
    const lastReading=multiReadingService.reading_ids.filter(id=>ids.includes(id)).at(-1);
    node('widgetservice'+i).value=multiReadingService.id;node('widgetservice'+i).onchange();
    node('widgetexample'+i).value=lastReading;node('widgetexample'+i).onchange();
    node('widgetuse'+i).onclick();
    check(node('widgetexample'+i).value===lastReading,'Use API preserves an explicitly selected reading belonging to that service');
    const draft=Object.fromEntries(['label','url','field','unit','interval'].map(key=>[key,node('widget'+key+i).value]));
    const mismatchedService=services.find(service=>service.id!==multiReadingService.id);
    node('widgetservice'+i).value=mismatchedService.id;node('widgetservice'+i).onchange();
    for(const key of Object.keys(draft))check(node('widget'+key+i).value===draft[key],'Browsing a different API preserves the current draft');
    check(node('widgetdraft'+i).classList.contains('bad'),'A browsed API that differs from the draft has an explicit warning');
    node('widgetsearch'+i).value='no-such-api-fixture';node('widgetsearch'+i).oninput();
    context.fixtureStatus=status();evaluate('showStatus(fixtureStatus)');
    for(const key of Object.keys(draft))check(node('widget'+key+i).value===draft[key],'Search and status polling preserve a pending draft');
    check(node('widgetservice'+i).value===mismatchedService.id&&node('widgetdraft'+i).classList.contains('bad'),'Search and polling preserve the service mismatch warning');
    const beforeBlocked=requests.length;
    await node('widget'+i).onsubmit({preventDefault(){}});
    check(requests.length===beforeBlocked&&node('widget'+i+'feedback').classList.contains('bad'),'Saving a different browsed service is blocked before network dispatch');
    check(/use|reading/i.test(node('widget'+i+'feedback').textContent),'Blocked save explains how to assign the browsed API to the custom widget');
    node('widgetsearch'+i).value='';node('widgetsearch'+i).oninput();
    const manualService=services.find(service=>!(service.reading_ids||[]).some(id=>ids.includes(id))&&service.auth_code!=='requires_key'&&service.fit_code!=='adapter');
    node('widgetservice'+i).value=manualService.id;node('widgetservice'+i).onchange();node('widgetuse'+i).onclick();
    node('widgeturl'+i).value='https://example.org/manual-'+i+'.json';node('widgeturl'+i).oninput();
    node('widgetfield'+i).value='data.0.reading';node('widgetfield'+i).oninput();
    requests=[];reply=async(path,options)=>path==='/api/widget'?{status:202,ok:true,json:async()=>({accepted:true})}:{status:200,ok:true,json:async()=>clone(status())};
    const manualSave=node('widget'+i).onsubmit({preventDefault(){}});
    check(node('widget'+i).querySelectorAll('button').every(button=>button.disabled),'Saving either widget disables all three of its actions');
    node('widgetuse'+i).onclick();
    check(node('widgeturl'+i).value==='https://example.org/manual-'+i+'.json','Use API cannot overwrite a draft while that widget is saving');
    await node('widget'+i).onsubmit({preventDefault(){}});
    check(requests.filter(request=>request.path==='/api/widget').length===1,'Repeated Save actions in either widget produce only one POST');
    await manualSave;
    const manualSubmission=requests.find(request=>request.path==='/api/widget');
    check(Boolean(manualSubmission),'A manual endpoint and field can be saved after Use API');
    const manualPayload=JSON.parse(manualSubmission.options.body);
    check(manualPayload.index===i&&manualPayload.url==='https://example.org/manual-'+i+'.json'&&manualPayload.field==='data.0.reading','Manual save submits the chosen widget and explicit endpoint and field');
    check(!node('widget'+i+'feedback').classList.contains('bad'),'Manual service save receives successful local feedback');
    check(node('widget'+i).querySelectorAll('button').every(button=>!button.disabled),'A successful save restores all eligible actions in either widget');
    check(node('widget'+i+'selectionfeedback').textContent===node('widget'+i+'feedback').textContent,'Save feedback appears beside the selector and detailed form in both widgets');
    node('widgetexample'+i).value='';node('widgetexample'+i).onchange();
    check(node('widgetservice'+i).value===''&&!evaluate('WIDGET_DRAFT_SERVICE[catalogSlot]'),'Choosing your own API clears catalog association');
  }
  // Native selects refuse a value absent from their current options. Applying a
  // reading must insert its associated service even under an unrelated filter.
  node('widgetsearch0').value='no-such-api-fixture';node('widgetsearch0').oninput();
  evaluate('applyExample(0,"bitcoin")');
  check(node('widgetexample0').value==='bitcoin','Applying a reading inserts its selected option under an unrelated search');
  check(node('widgetservice0').value===evaluate('READING_SERVICE_INDEX.get("bitcoin")'),'Applying a reading inserts its associated service under an unrelated search');
  node('widgetsearch0').value='';node('widgetsearch0').oninput();
  context.fixtureStatus={...status(),latitude:0,longitude:0};evaluate('showStatus(fixtureStatus)');
  evaluate('applyExample(0,"humidity")');
  check(node('widgeturl0').value.includes('latitude=0.0000')&&node('widgeturl0').value.includes('longitude=0.0000'),'Saved-city presets accept genuine zero coordinates');
  context.fixtureStatus=status();evaluate('showStatus(fixtureStatus)');
  context.saved=status();context.saved.widgetConfig[0]={...context.saved.widgetConfig[0],url:'https://api.coinbase.com/v2/prices/BTC-USD/spot',field:'data.amount'};
  evaluate('first=true;showStatus(saved)');
  check(node('widgetexample0').value==='bitcoin','Reload recognizes an existing saved catalog source without rewriting it');
  check(node('widgetlabel0').value==='Original one','Recognizing a preset preserves a custom display label');
  evaluate('applyExample(0,"bitcoin")');node('widgetexample0').value='bitcoin';
  node('widgetsearch0').value='Coinbase';node('widgetsearch0').oninput();
  node('widgeturl0').value='https://example.org/custom.json';node('widgeturl0').oninput();
  check(node('widgetexample0').value===''&&node('widgetdocs0').classList.contains('hide'),'Editing a source URL clears misleading provider attribution');
  check(node('widgetsearch0').value==='Coinbase'&&node('widgeturl0').value==='https://example.org/custom.json','Clearing source attribution preserves search and custom edits');
  evaluate('applyExample(0,"bitcoin")');node('widgetexample0').value='bitcoin';
  node('widgetfield0').value='data.custom';node('widgetfield0').oninput();
  check(node('widgetexample0').value===''&&node('widgetfield0').value==='data.custom','Editing the selected field clears preset association without discarding it');
  const priorUrl=node('widgeturl0').value,priorLabel=node('widgetlabel0').value;
  context.fixtureStatus={...status(),latitude:91,longitude:0};evaluate('showStatus(fixtureStatus);applyExample(0,"humidity")');
  check(node('widgeturl0').value===priorUrl&&node('widgetlabel0').value===priorLabel&&node('widget0feedback').classList.contains('bad'),'Out-of-range saved-city latitude rejects selection without mutating fields');
  context.fixtureStatus={...status(),latitude:0,longitude:-181};evaluate('showStatus(fixtureStatus);applyExample(0,"humidity")');
  check(node('widgeturl0').value===priorUrl,'Out-of-range saved-city longitude also preserves fields');
  context.fixtureStatus=status();evaluate('showStatus(fixtureStatus)');
  node('widgetsearch0').value='';node('widgetsearch0').oninput();
  const unchangedTwo=node('widgeturl1').value;
  evaluate('applyExample(0,"bitcoin")');
  check(node('widgeturl1').value===unchangedTwo,'Example assignment does not change the other slot');
  node('widgetlabel0').value='Unsaved label';node('widgetfield0').value='edited.0.value';node('widgeturl0').value='https://example.org/edited.json';node('widgetenabled0').checked=false;
  context.fixtureStatus=status();evaluate('showStatus(fixtureStatus)');
  check(node('widgetlabel0').value==='Unsaved label'&&node('widgetfield0').value==='edited.0.value'&&node('widgetenabled0').checked===false,'Polling preserves unsaved widget edits');

  requests=[];reply=async(path,options)=>path==='/api/widget'?{status:202,ok:true,json:async()=>({accepted:true})}:{status:200,ok:true,json:async()=>clone(status())};
  node('widgetenabled0').checked=true;node('widgetinterval0').value='300';node('widgetunit0').value='%';
  await node('widget0').onsubmit({preventDefault(){}});
  const submission=requests.find(request=>request.path==='/api/widget');
  check(Boolean(submission),'Widget form dispatches a configuration');
  const payload=JSON.parse(submission.options.body);
  check(payload.index===0&&payload.enabled===true&&payload.interval===300,'Submitted slot, boolean and whole interval are typed correctly');
  check(payload.field==='edited.0.value'&&payload.url==='https://example.org/edited.json','Submitted configuration uses current edits');
  check(node('widget0feedback').textContent.includes('Configuration accepted')&&!node('widget0').button.disabled,'Save feedback stays beside its form and button becomes usable');

  requests=[];reply=async()=>({status:400,ok:false,json:async()=>({error:'Use a scalar field.'})});
  await node('widget1').onsubmit({preventDefault(){}});
  check(node('widget1feedback').textContent==='Use a scalar field.'&&node('widget1feedback').classList.contains('bad'),'Rejected second widget reports its own error');
  check(!node('widget1').button.disabled,'Rejected save does not leave the form busy');

  reply=async()=>({status:200,ok:true,json:async()=>{throw SyntaxError('offline fixture invalid JSON')}});
  await node('widget1').onsubmit({preventDefault(){}});
  check(node('widget1feedback').textContent.includes('unreadable response')&&node('widget1feedback').classList.contains('bad'),'Invalid JSON response produces a readable local form error');
  check(!node('widget1').button.disabled,'Unreadable response does not leave the form busy');

  reply=async()=>{throw Error('offline fixture transport')};await evaluate('poll()');
  check(node('widgetstate0').textContent.includes('Device unavailable')&&node('widgetstate1').textContent.includes('Device unavailable'),'A transport interruption is visible for both widgets');
  reply=async()=>({status:401,ok:false,json:async()=>({error:'Pair again.'})});
  await evaluate('poll()');
  check(node('desk').classList.contains('hide')&&!node('pair').classList.contains('hide'),'Expired session returns to pairing');
  context.fixtureStatus=status();evaluate('showStatus(fixtureStatus)');
  check(node('widgetlabel0').value==='Original one'&&node('widgetfield0').value==='data.0.price','A new paired session initializes fields from saved configuration');

  requests=[];let resolveDelayed;
  reply=async()=>new Promise(resolve=>{resolveDelayed=resolve});
  const firstPoll=evaluate('poll()'),secondPoll=evaluate('poll()');
  check(requests.length===1,'Concurrent paired polls share one network request');
  resolveDelayed({status:200,ok:true,json:async()=>clone(status())});await firstPoll;await secondPoll;
  check(evaluate('pollPromise===null'),'Completed shared poll releases its in-flight guard');

  requests=[];reply=async()=>new Promise(resolve=>{resolveDelayed=resolve});
  const stalePoll=evaluate('poll()');
  context.fixtureStatus=status();context.fixtureStatus.csrf='offline-new-session-placeholder';evaluate('showStatus(fixtureStatus)');
  resolveDelayed({status:401,ok:false,json:async()=>({error:'Old session expired.'})});await stalePoll;
  check(!node('desk').classList.contains('hide')&&node('pair').classList.contains('hide'),'An old pending request cannot clear a newer paired session');
  check(evaluate('csrf')==='offline-new-session-placeholder','Old-session response retains the current session token');

  reply=async(path,options)=>new Promise((resolve,reject)=>options.signal.addEventListener('abort',()=>reject(Object.assign(Error('offline abort fixture'),{name:'AbortError'})),{once:true}));
  requests=[];
  const timedOutSave=node('widget1').onsubmit({preventDefault(){}});
  check(node('widget1').querySelectorAll('button').every(button=>button.disabled),'Pending save disables Use API and both Save actions');
  await node('widget1').onsubmit({preventDefault(){}});
  check(requests.length===1,'Two submissions from the same widget share one configuration request');
  check(!node('widget0').button.disabled,'Saving one widget does not disable the other widget');
  const deadlineTimer=[...timers.values()].find(timer=>timer.delay===15000);
  check(Boolean(deadlineTimer),'Fetch receives the configured bounded timeout');
  deadlineTimer.callback();await timedOutSave;
  check(node('widget1feedback').textContent.includes('timed out')&&!node('widget1').button.disabled,'Abort timeout produces a readable form error and releases the button');
  check(!node('widgetsavetop1').disabled&&node('widget1selectionfeedback').textContent===node('widget1feedback').textContent,'Timeout releases the nearby Save action and mirrors its error beside the selector');
  check(node('widget1').dataset.busy==='false','Timeout clears the form submission guard');
  check(timers.size===0,'All request deadline timers are cleaned up');
  console.log('PASS: '+assertions+' exact embedded-JS DOM assertions (offline fixtures; Safari/device checks separate)');
}
main().catch(error=>{console.error(error.message);process.exitCode=1});
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--node", default="node")
    args = parser.parse_args()
    source = (ROOT / "firmware/AuraDesk/web_service.cpp").read_text()
    for slot in range(2):
        form = re.search(rf'<form id="widget{slot}"[^>]*>([\s\S]*?)</form>', source)
        if not form:
            print(f"FAIL: Widget {slot + 1} form is missing", file=sys.stderr)
            return 1
        buttons = [dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))
                   for attrs in re.findall(r'<button\b([^>]*)>', form.group(1))]
        use = next((button for button in buttons if button.get("id") == f"widgetuse{slot}"), {})
        top_save = next((button for button in buttons if button.get("id") == f"widgetsavetop{slot}"), {})
        if len(buttons) != 3 or use.get("type") != "button" or top_save.get("type") != "submit":
            print(f"FAIL: Widget {slot + 1} requires explicit Use and two native Save actions", file=sys.stderr)
            return 1
        if sum(button.get("type") == "submit" for button in buttons) != 2:
            print(f"FAIL: Widget {slot + 1} Save actions must share its native submit handler", file=sys.stderr)
            return 1
        if not all(f'id="{identifier}"' in form.group(1)
                   for identifier in (f"widgetdraft{slot}", f"widget{slot}selectionfeedback")):
            print(f"FAIL: Widget {slot + 1} requires draft and nearby Save feedback", file=sys.stderr)
            return 1
    included = (ROOT / "firmware/AuraDesk/api_services.js.inc").read_text()
    raw_literals = re.findall(r'R"([^ ()\\\t\r\n]{0,16})\(([\s\S]*?)\)\1"', included)
    if not raw_literals:
        print("FAIL: Service catalog must contain adjacent raw string literals", file=sys.stderr)
        return 1
    include_script = "".join(body for delimiter, body in raw_literals)
    splice = ')AURA"\n#include "api_services.js.inc"\nR"AURA('
    if source.count(splice) != 1:
        print("FAIL: Expected exactly one service catalog string splice", file=sys.stderr)
        return 1
    source = source.replace(splice, include_script)
    scripts = re.findall(r"<script>([\s\S]*?)</script>", source)
    if len(scripts) != 1:
        print("FAIL: Exactly one embedded browser script is required", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory(prefix="aura-widget-browser-") as directory:
        script = Path(directory) / "embedded.js"
        harness = Path(directory) / "checks.cjs"
        script.write_text(scripts[0])
        harness.write_text(HARNESS)
        script.chmod(0o600)
        harness.chmod(0o600)
        checked = subprocess.run([args.node, str(harness), str(script)], capture_output=True, text=True)
        print(checked.stdout, end="")
        print(checked.stderr.replace(str(ROOT), "<workspace>").replace(directory, "<temporary>"),
              file=sys.stderr, end="")
        return checked.returncode


if __name__ == "__main__":
    raise SystemExit(main())
