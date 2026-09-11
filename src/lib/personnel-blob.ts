import {get,put} from '@vercel/blob';
import {readWeatherStream} from './weather-blob';
import {PERSONNEL_POINTER,type PersonnelObjectStore} from './personnel-publication';

export function personnelBlobPath(path:string){
  if(!/^personnel\/(latest\.json|objects\/[a-f0-9]{64})$/.test(path))throw Error('Invalid personnel storage path');
  return path;
}

export const personnelBlobStore:PersonnelObjectStore={
  async read(path){
    const result=await get(personnelBlobPath(path),{access:'private',useCache:false,abortSignal:AbortSignal.timeout(5000)});
    if(!result)return null;
    if(result.statusCode!==200||!result.blob.etag)throw Error('Invalid stored personnel response');
    return {body:await readWeatherStream(result.stream,result.blob.size===0?null:result.blob.size),etag:result.blob.etag};
  },
  async write(path,body,etag){
    personnelBlobPath(path);
    if(body.length<1||body.length>10_000_000)throw Error('Invalid personnel object size');
    if(path!==PERSONNEL_POINTER&&etag!==undefined)throw Error('Personnel archives cannot be overwritten');
    if(etag!==undefined&&!etag)throw Error('Personnel pointer version required');
    await put(path,body,{access:'private',allowOverwrite:etag!==undefined,ifMatch:etag,
      addRandomSuffix:false,contentType:'application/octet-stream',abortSignal:AbortSignal.timeout(5000)});
  },
};
