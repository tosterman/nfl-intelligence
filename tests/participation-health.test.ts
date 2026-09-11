import { test } from 'node:test';
import assert from 'node:assert/strict';
import { participationHealth } from '../src/lib/participation-health';
const at='2026-09-11T16:00:00Z', hash='a'.repeat(64), now=Date.parse(at);
const source={status:'available',season:2026,sourceHash:hash,retrievedAt:at,rows:187};
const collection={status:'collected',season:2026,sourceHash:hash,retrievedAt:at,attemptedAt:at};
const personnel={sourceHash:'b'.repeat(64),retrievedAt:at};
const artifact={sourceSeason:2026,sourceHash:hash,sourceRetrievedAt:at,calculatedAt:at,personnelSourceHash:personnel.sourceHash,personnelRetrievedAt:at};
test('fresh bound acquisition does not require an eligible weekly sample',()=> {
  assert.equal(participationHealth(source,collection,artifact,personnel,2026,now).status,'ok');
  assert.equal(participationHealth(source,collection,artifact,personnel,2026,now+30*3600000).status,'unavailable');
});
test('failed collection, source mismatch and report rollover cannot report healthy',()=> {
  for(const change of [{status:'failed'},{sourceHash:'c'.repeat(64)},{retrievedAt:'2027-01-01T00:00:00Z'},{season:2027}])
    assert.equal(participationHealth(source,{...collection,...change},artifact,personnel,2026,now).status,'unavailable');
  assert.equal(participationHealth(source,collection,artifact,{...personnel,sourceHash:'c'.repeat(64)},2026,now).status,'unavailable');
  assert.equal(participationHealth(source,collection,{...artifact,calculatedAt:'bad'},personnel,2026,now).status,'unavailable');
});
