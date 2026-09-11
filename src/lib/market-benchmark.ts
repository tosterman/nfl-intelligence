export type BenchmarkBook = { book:string; market:'spread'|'total'; pairedGames:number;
  modelMae:number|null; marketMae:number|null; excludedGames:number; exclusionReasons:Record<string,number> };
export type MarketBenchmark = {schemaVersion:1; checkedAt:string; coverageThrough:string; scopeGames:number;
  closingCheckpointCounts:Record<string,number>; pairedGameCount:number; excludedBookMarketCount:number; excludedGameCount:number; books:BenchmarkBook[]; reportHash:string};
const object=(value:unknown):value is Record<string,unknown>=>!!value&&typeof value==='object'&&!Array.isArray(value);
const count=(value:unknown):value is number=>Number.isSafeInteger(value)&&Number(value)>=0;
export function parseMarketBenchmark(raw:unknown,now:number):MarketBenchmark|null {
  if(!object(raw)||raw.schemaVersion!==1||typeof raw.reportHash!=='string'||!/^[a-f0-9]{64}$/.test(raw.reportHash)||
    typeof raw.checkedAt!=='string'||typeof raw.coverageThrough!=='string'||!count(raw.scopeGames)||raw.scopeGames>1000||
    !count(raw.pairedGameCount)||raw.pairedGameCount>raw.scopeGames||!count(raw.excludedBookMarketCount)||!count(raw.excludedGameCount)||
    raw.excludedGameCount>raw.scopeGames||raw.excludedGameCount>raw.excludedBookMarketCount||
    !Array.isArray(raw.books)||raw.books.length>200||!object(raw.closingCheckpointCounts))return null;
  const checked=Date.parse(raw.checkedAt),coverage=Date.parse(raw.coverageThrough);
  if(![checked,coverage,now].every(Number.isFinite)||coverage>checked||checked>now||
    ![raw.checkedAt,raw.coverageThrough].every(value=>/(Z|[+-]\d\d:\d\d)$/.test(value)))return null;
  const checkpoints=Object.values(raw.closingCheckpointCounts);
  if(checkpoints.some(v=>!count(v))||checkpoints.reduce<number>((sum,v)=>sum+Number(v),0)!==raw.scopeGames)return null;
  const seen=new Set<string>();
  for(const row of raw.books){
    if(!object(row)||typeof row.book!=='string'||!/^[a-z0-9_-]{1,60}$/.test(row.book)||!['spread','total'].includes(String(row.market))||
      !count(row.pairedGames)||!count(row.excludedGames)||row.pairedGames+row.excludedGames>raw.scopeGames||row.pairedGames>raw.pairedGameCount||
      !object(row.exclusionReasons)||Object.values(row.exclusionReasons).some(v=>!count(v)||v>Number(row.excludedGames)))return null;
    if([row.modelMae,row.marketMae].some(v=>row.pairedGames===0?v!==null:typeof v!=='number'||!Number.isFinite(v)||v<0))return null;
    const key=`${row.book}:${row.market}`;if(seen.has(key))return null;seen.add(key);
  }
  if(raw.pairedGameCount>raw.books.reduce((sum,row)=>sum+row.pairedGames,0))return null;
  if(raw.excludedBookMarketCount!==raw.books.reduce((sum,row)=>sum+row.excludedGames,0)||
    raw.excludedBookMarketCount>0&&raw.excludedGameCount===0)return null;
  return raw as unknown as MarketBenchmark;
}
