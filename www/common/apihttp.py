#apihttp
import aiohttp 
import asyncio
from log import Log
import json

@asyncio.coroutine
async def http_post(url, data):
    try:
        if url is None:
            return;

        if data is None:
            return;
        
        _data = json.dumps(data)
        Log.info('%s,%s'%(url, _data));
        headers = {'content-type':'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data = _data, headers=headers) as res:
                status = res.status
                if res.content_type == 'application/json':
                    return await res.json()
                if res.content_type == 'text/xml':
                    return res.text()
                if res.content_type == 'application/x-www-form-urlencoded':
                    return res.text()
                    return resp

    except Exception as ex:
        print(ex)
        return;


