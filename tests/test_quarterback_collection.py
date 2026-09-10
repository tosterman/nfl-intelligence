import csv,gzip,hashlib,io,json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import refresh_quarterbacks as qb
ROOT=Path(__file__).resolve().parents[1]
class QuarterbackCollectionTests(unittest.TestCase):
 def test_source_and_normalized_roles_are_reproducible(self):
  snapshot=json.loads((ROOT/'data/quarterbacks.json').read_text())
  folder=ROOT/'data/quarterback-sources';manifest=json.loads((folder/(snapshot['sourceHash']+'.manifest.json')).read_text())
  blocks=[gzip.decompress((folder/'raw-chunks'/(h+'.gz')).read_bytes()) for h in manifest['chunks']]
  for h,block in zip(manifest['chunks'],blocks):self.assertEqual(hashlib.sha256(block).hexdigest(),h)
  raw=b''.join(blocks)
  self.assertEqual(len(raw),manifest['bytes'])
  self.assertEqual(hashlib.sha256(raw).hexdigest(),snapshot['sourceHash'])
  self.assertEqual(qb.normalize(raw,set(snapshot['teams']),qb.instant(snapshot['retrievedAt'])),snapshot['teams'])
 def test_bad_source_schema_fails(self):
  with self.assertRaises(ValueError):qb.normalize(b'wrong,column\nx,y\n',{'A'},qb.instant('2026-09-10T12:00:00Z'))
 def test_unchanged_timestamp_blocks_are_reused_byte_for_byte(self):
  old=b'dt,team\r\n2026-09-09T12:00:00Z,A\r\n'
  new=b'dt,team\r\n2026-09-10T12:00:00Z,B\r\n'+old.split(b'\r\n',1)[1]
  with tempfile.TemporaryDirectory() as temp:
   folder=Path(temp);first=qb.archive_source(old,folder);second=qb.archive_source(new,folder)
   self.assertEqual(first['chunks'][0],second['chunks'][0]);self.assertEqual(first['chunks'][1],second['chunks'][2])
   self.assertEqual(len(list((folder/'raw-chunks').glob('*.gz'))),3)
   self.assertEqual(b''.join(gzip.decompress((folder/'raw-chunks'/(h+'.gz')).read_bytes()) for h in second['chunks']),new)
 def test_failure_preserves_last_snapshot_and_records_unavailable(self):
  with tempfile.TemporaryDirectory() as folder,patch.object(qb,'ROOT',Path(folder)),patch.object(qb,'main',side_effect=ValueError('bad source')):
   p=Path(folder)/'data';p.mkdir();target=p/'quarterbacks.json';target.write_text('previous')
   self.assertEqual(qb.run_collection(),1)
   self.assertEqual(target.read_text(),'previous')
   self.assertEqual(json.loads((p/'quarterback-collection.json').read_text())['status'],'unavailable')
