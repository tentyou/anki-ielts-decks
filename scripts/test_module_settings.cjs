const fs=require('fs'),vm=require('vm');
const keys=['frequency','wordAudio','ipa','meaning','englishDefinition','morphology','wordFamily','derivatives','examples','examExamples','sources'];
const source=fs.readFileSync('templates/module-settings.js','utf8');
for(const target of [null,...keys]){
 const nodes=keys.map(key=>({hidden:null,getAttribute:()=>key}));
 const ctx={document:{querySelectorAll:()=>[{querySelectorAll:()=>nodes}]}};
 vm.runInNewContext(target?source.replace(target+': true',target+': false'):source,ctx);
 nodes.forEach((node,i)=>{if(node.hidden!==(keys[i]===target))throw Error('Switch failed: '+target);});
}
console.log('PASS: 11 switches individually hide their module; default all visible.');
