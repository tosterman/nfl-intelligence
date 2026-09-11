import { createRoot } from 'react-dom/client';
import { MarketCard, MarketPanel } from '../../src/components/market-panel';
import site from '../../data/site.json';
import { WeatherExpiry } from '../../src/components/weather-expiry';
import { PersonnelExpiry } from '../../src/components/personnel-expiry';
const game={home:'LA',away:'SF',kickoff:'2026-09-10T18:00:00Z',status:'scheduled'};
const pair={homePrice:-110,awayPrice:-110};
const feed={state:'ready' as const,fetchedAt:'2026-09-10T10:01:00Z',events:[{...game,id:'fixture',books:[{book:'fixture',name:'Fixture Book',spread:{...pair,observedAt:'2026-09-10T10:00:00Z',homePoint:-3.5},total:{observedAt:'2026-09-10T10:00:20Z',point:48.5,overPrice:-110,underPrice:-110},moneyline:null}]}]};
const prediction=site.games.find(g=>g.snapshot)!.snapshot!.prediction;
const contextRoot=document.createElement('div');document.body.append(contextRoot);
const expiry=Date.parse('2026-09-10T15:59:59.500Z');
createRoot(contextRoot).render(<><div id='weather'><WeatherExpiry expiresAt={expiry}>Weather fixture</WeatherExpiry></div><div id='personnel'><PersonnelExpiry expiresAt={expiry}>Personnel fixture</PersonnelExpiry></div></>);
createRoot(document.getElementById('root')!).render(<><div id='card'><MarketCard game={game} feed={feed} initialNow={Date.now()} prediction={prediction} freshness={[{name:"Model",retrievedAt:"2026-09-09T10:00:00Z"}]}/></div><MarketPanel game={game} feed={feed} prediction={prediction} freshness={[{name:'Model',retrievedAt:'2026-09-09T10:00:00Z'}]} initialNow={Date.now()}/></>);

