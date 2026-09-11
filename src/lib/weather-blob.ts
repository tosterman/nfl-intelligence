import {get,put} from '@vercel/blob';
import type {WeatherObjectStore} from './weather-publication';

export function weatherBlobPath(path:string){
  if(!/^weather\/(latest\.json|objects\/[a-f0-9]{64}|manifests\/[a-f0-9]{64}\.json)$/.test(path))throw Error('Invalid weather storage path');
  return path;
}

export async function readWeatherStream(stream:ReadableStream<Uint8Array>,size:number|null){
  const reader=stream.getReader();const chunks:Buffer[]=[];let bytes=0;
  try{
    if(size!==null&&(!Number.isSafeInteger(size)||size<1||size>10_000_000))throw Error('Invalid weather object size');
    for(;;){
      const {done,value}=await reader.read();if(done)break;
      bytes+=value.byteLength;if(bytes>(size??10_000_000))throw Error('Weather stream exceeds declared size');
      chunks.push(Buffer.from(value));
    }
    if(!bytes||(size!==null&&bytes!==size))throw Error('Weather stream size mismatch');
    return Buffer.concat(chunks,bytes);
  }catch(error){await reader.cancel().catch(()=>{});throw error;}
  finally{reader.releaseLock();}
}

export const weatherBlobStore:WeatherObjectStore={
  async read(path){
    const result=await get(weatherBlobPath(path),{access:'private',useCache:false,abortSignal:AbortSignal.timeout(5000)});
    if(!result)return null;
    if(result.statusCode!==200||!result.blob.etag)throw Error('Invalid stored weather response');
    // SDK reports zero when Content-Length is absent on a chunked private read.
    return {body:await readWeatherStream(result.stream,result.blob.size===0?null:result.blob.size),etag:result.blob.etag};
  },
  async write(path,body,etag){
    weatherBlobPath(path);
    if(body.length<1||body.length>10_000_000)throw Error('Invalid weather object size');
    if(path!=='weather/latest.json'&&etag!==undefined)throw Error('Weather archives cannot be overwritten');
    if(etag!==undefined&&!etag)throw Error('Weather pointer version required');
    await put(path,body,{access:'private',allowOverwrite:etag!==undefined,ifMatch:etag,
      addRandomSuffix:false,contentType:'application/octet-stream',abortSignal:AbortSignal.timeout(5000)});
  },
};
