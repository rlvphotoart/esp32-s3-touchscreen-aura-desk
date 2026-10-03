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
  constructor(id){this.id=id;this.textContent='';this.value='';this.checked=false;this.disabled=false;this.className='';this.type='';this.files=[];this.button={disabled:false};this.children=[];
    this.classList={add:(...names)=>{const current=new Set(this.className.split(/\s+/).filter(Boolean));names.forEach(n=>current.add(n));this.className=[...current].join(' ')},remove:(...names)=>{this.className=this.className.split(/\s+/).filter(n=>n&&!names.includes(n)).join(' ')},contains:name=>this.className.split(/\s+/).includes(name)};
  }
  querySelector(selector){if(selector==='button')return this.button;throw Error('Unknown DOM selector in offline harness')}
  appendChild(node){this.children.push(node);return node}
  click(){}
}
const nodes=new Map();
const node=id=>{if(!nodes.has(id))nodes.set(id,new Element(id));return nodes.get(id)};
let requests=[],reply=async()=>({status:401,ok:false,json:async()=>({error:'Pair again.'})});
let nextTimer=1;const timers=new Map(),intervals=[];
const context={document:{getElementById:node,createElement:tag=>new Element(tag)},fetch:async(path,options)=>{requests.push({path,options});return reply(path,options)},AbortController,setInterval:callback=>{intervals.push(callback);return intervals.length},setTimeout:(callback,delay)=>{const id=nextTimer++;timers.set(id,{callback,delay});return id},clearTimeout:id=>timers.delete(id),Blob:class {},URL:{createObjectURL:()=>'',revokeObjectURL:()=>{}},XMLHttpRequest:class {}};
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
    if(example==='bitcoin')check(node('widgetfield0').value==='data.0.quotes.0.price','Public price example selects nested arrays correctly');
    if(example==='carbon')check(node('widgetfield0').value==='data.0.intensity.forecast','Carbon example selects array item zero');
    if(example==='eurRon')check(node('widgetfield0').value==='rates.RON','Currency example selects the named rate');
    if(example==='humidity')check(node('widgeturl0').value.includes('latitude=12.3457')&&node('widgeturl0').value.includes('longitude=-45.6789'),'City example uses current saved coordinates');
  }
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
  const timedOutSave=node('widget1').onsubmit({preventDefault(){}});
  check(node('widget1').button.disabled,'Pending save prevents duplicate submissions');
  const deadlineTimer=[...timers.values()].find(timer=>timer.delay===15000);
  check(Boolean(deadlineTimer),'Fetch receives the configured bounded timeout');
  deadlineTimer.callback();await timedOutSave;
  check(node('widget1feedback').textContent.includes('timed out')&&!node('widget1').button.disabled,'Abort timeout produces a readable form error and releases the button');
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
