import { test } from "node:test";
import assert from "node:assert/strict";
import { quarterbackForGame, type QuarterbackSnapshot } from "../src/lib/quarterbacks";
const at="2026-09-10T12:00:00Z",now=Date.parse(at);
const game={season:2026,status:"scheduled",kickoff:"2026-09-11T12:00:00Z"};
const snapshot:QuarterbackSnapshot={season:2026,retrievedAt:at,assetUpdatedAt:at,sourceUrl:"https://example.com",sourceHash:"a".repeat(64),teams:{A:{status:"available",recordedAt:at,listedFirst:"p",quarterbacks:[{playerId:"p",name:"Player",rank:1}]}}};
test("listed QB requires matching season, team, pregame time and fresh source",()=>{
 assert.equal(quarterbackForGame(snapshot,game,"A",now)?.name,"Player");
 assert.equal(quarterbackForGame(snapshot,game,"B",now),null);
 assert.equal(quarterbackForGame(snapshot,{...game,season:2025},"A",now),null);
 assert.equal(quarterbackForGame(snapshot,{...game,status:"final"},"A",now),null);
 assert.equal(quarterbackForGame(snapshot,game,"A",Date.parse(game.kickoff)),null);
 for(const field of ["retrievedAt","assetUpdatedAt"]){
  assert.equal(quarterbackForGame({...snapshot,[field]:"2026-09-08T12:00:00Z"},game,"A",now),null);
  assert.equal(quarterbackForGame({...snapshot,[field]:"2026-09-10T12:00:01Z"},game,"A",now),null);
 }
});
test("provider record time expires independently and conflicting identity names are withheld",()=>{
 const role=snapshot.teams.A;
 assert.equal(quarterbackForGame({...snapshot,teams:{A:{...role,recordedAt:"2026-09-08T12:00:00Z"}}},game,"A",now),null);
 assert.equal(quarterbackForGame({...snapshot,teams:{A:{...role,quarterbacks:[...role.quarterbacks,{playerId:"p",name:"Other name",rank:1}]}}},game,"A",now),null);
 assert.equal(quarterbackForGame(snapshot,game,"A",now)?.expiresAt,Date.parse(game.kickoff));
});
