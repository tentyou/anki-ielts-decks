// Behavioral tests for review-webview caching, retries, and version comparison.
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const source = fs.readFileSync('templates/update-check.js', 'utf8');
const now = 1800000000000;
function environment({cache, blocked=false, hidden=false, current='0.3.1'}={}) {
  const button = {}, link = {}, status = {textContent:''};
  const element = {hidden, querySelector: s => ({'.check-update':button,'.release-link':link,'.update-status':status}[s])};
  const requests = [];
  const store = cache ? JSON.stringify(cache) : null;
  const storage = {value:store,getItem(){if(blocked) throw Error('denied');return this.value;},setItem(k,v){if(blocked)throw Error('denied');this.value=v;}};
  function XHR() { requests.push(this); }
  XHR.prototype.open = function(method,url,async) {this.url=url;assert.equal(method,'GET');assert.equal(async,true);};
  XHR.prototype.send = function() {};
  const context = vm.createContext({window:{},document:{querySelectorAll:()=>[element],contains:()=>true},localStorage:storage,XMLHttpRequest:XHR,Date:{now:()=>now}});
  function run(){vm.runInContext(source.replace('__DECK_VERSION__',current),context);}
  function respond(tag='v0.3.1',extra={}){const x=requests.at(-1);x.status=200;x.responseText=JSON.stringify({tag_name:tag,...extra});x.onload();}
  run();return {button,link,status,requests,storage,respond,run};
}
let e=environment();assert.equal(e.requests.length,1);assert.equal(e.requests[0].timeout,6000);
assert.equal(e.requests[0].url,'https://api.github.com/repos/tentyou/anki-ielts-decks/releases/latest');
e.respond('v0.10.0');assert.match(e.link.textContent,/发现 v0.10.0/);assert.equal(e.status.textContent,'');
e.run();assert.equal(e.requests.length,1);e.button.onclick();assert.equal(e.requests.length,2);e.respond('v0.3.1');assert.equal(e.status.textContent,'当前已是最新版本。');
e=environment({current:'0.10.0'});e.respond('v0.9.0');assert.equal(e.link.textContent,'版本与下载');
e=environment({cache:{at:now,ok:true,latest:'v0.4.0'}});assert.equal(e.requests.length,0);assert.match(e.link.textContent,/发现/);
e=environment({cache:{at:now-86400001,ok:true,latest:'v0.4.0'}});assert.equal(e.requests.length,1);e.requests[0].ontimeout();assert.match(e.link.textContent,/v0.4.0/);e.run();assert.equal(e.requests.length,1);e.button.onclick();assert.equal(e.requests.length,2);e.requests[1].onerror();assert.match(e.status.textContent,/暂时无法/);
e=environment({blocked:true});e.respond();e.run();assert.equal(e.requests.length,1);
e=environment({hidden:true});assert.equal(e.requests.length,0);
e=environment();e.run();assert.equal(e.requests.length,1);e.respond();assert.equal(e.button.disabled,false);
for(const [tag,extra] of [['v0.4.0-beta',{}],['v0.4.0',{prerelease:true}],['<script>',{}],['v0.4.0',{draft:true}]]) {
  e=environment();e.respond(tag,extra);assert.equal(e.link.textContent,'版本与下载');
}
e=environment();e.requests[0].responseText='not JSON';e.requests[0].status=403;e.requests[0].onload();assert.equal(e.button.disabled,false);
console.log('PASS: numeric versions, daily cache, manual refresh, timeout/offline, blocked storage, hidden module, shared request, invalid releases.');
