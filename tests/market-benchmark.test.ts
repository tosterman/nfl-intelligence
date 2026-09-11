import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createElement} from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
import {parseMarketBenchmark} from '../src/lib/market-benchmark';
import {MarketBenchmarkPanel} from '../src/components/market-benchmark';
import real from '../data/market-benchmark.json';
const now=Date.parse(real.checkedAt)+1000;
const render=(data:unknown)=>renderToStaticMarkup(createElement(MarketBenchmarkPanel,{data,now}));
test('real empty benchmark distinguishes missing evidence from zero error',()=>{
  assert.ok(parseMarketBenchmark(real,now));
  const html=render(real);
  assert.match(html,/No eligible completed comparisons yet/);
  assert.match(html,/Reasons may overlap/);
  assert.match(html,/18 sportsbook-and-market entries excluded across 1 game/);
  assert.doesNotMatch(html,/<table/);
  assert.match(html,/Capture outside the required time window/);
});
test('invalid dates, counts, duplicate rows and zero-game averages fail closed',()=>{
  for(const patch of [{checkedAt:'2199-01-01T00:00:00Z'},{checkedAt:'2026-09-11T19:00:00'},
    {scopeGames:real.scopeGames+1},{pairedGameCount:1},
    {books:[...real.books,real.books[0]]},
    {books:[{...real.books[0],modelMae:0}]}])assert.equal(parseMarketBenchmark({...real,...patch},now),null);
  assert.match(render(null),/report is unavailable/);
  assert.doesNotMatch(render(null),/No eligible completed comparisons/);
});
test('positive fixture shows same-game per-book errors and explicit units',()=>{
  const data={...real,pairedGameCount:1,excludedBookMarketCount:0,excludedGameCount:0,books:[{book:'example',market:'spread',pairedGames:1,excludedGames:0,modelMae:1.25,marketMae:2.5,exclusionReasons:{}}]};
  const html=render(data);
  assert.match(html,/identical games within each row/);
  assert.match(html,/1\.25/);assert.match(html,/2\.50/);
  assert.match(html,/24 hours before kickoff/);
  assert.match(html,/not measure betting returns/);
});
