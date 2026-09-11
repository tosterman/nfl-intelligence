import {test} from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import ts from 'typescript';

test('generated personnel JSON supports different changed fields in different rows',()=>{
 const root=process.cwd();
 const config=ts.readConfigFile(path.join(root,'tsconfig.json'),ts.sys.readFile);
 const parsed=ts.parseJsonConfigFileContent(config.config,ts.sys,root);
 const options={...parsed.options,noEmit:true,incremental:false};
 const host=ts.createCompilerHost(options),read=host.readFile.bind(host);
 const common={season:2026,type:'REG',week:1,team:'ATL',playerId:'fixture',kind:'changed',
  observedAfter:'2026-09-11T10:00:00Z',observedBy:'2026-09-11T11:00:00Z',eventTime:null,
  playerName:'Fixture player',position:'QB'};
 const fixture=JSON.stringify({schemaVersion:1,sourceHash:'a'.repeat(64),
  retrievedAt:common.observedBy,previousRetrievedAt:common.observedAfter,
  changes:[{...common,fields:{practiceStatus:{before:'Full',after:'Limited'}}},
   {...common,playerId:'second-fixture',fields:{reportStatus:{before:null,after:'Questionable'}}}]});
 const target=path.normalize(path.join(root,'data/personnel-changes.json'));
 // Override compiler input only: do not mutate the live site's data files.
 host.readFile=file=>path.normalize(file)===target?fixture:read(file);
 const program=ts.createProgram([path.join(root,'src/lib/personnel-static.ts')],options,host);
 const diagnostics=ts.getPreEmitDiagnostics(program);
 assert.equal(diagnostics.length,0,diagnostics.map(d=>ts.flattenDiagnosticMessageText(d.messageText,'\n')).join('\n'));
});
