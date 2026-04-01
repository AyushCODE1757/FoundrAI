import asyncio
import json
from agents import run_ceo_agent, run_dev_agent, run_marketing_agent, run_finance_agent

async def wrap_task(name, coro):
    res = await coro
    return name, res

async def run_simulation_stream(idea: str):
    # Start
    yield f"data: {json.dumps({'agent': 'System', 'status': 'started'})}\n\n"
    
    # CEO
    yield f"data: {json.dumps({'agent': 'CEO', 'status': 'working'})}\n\n"
    ceo_output = await asyncio.to_thread(run_ceo_agent, idea)
    yield f"data: {json.dumps({'agent': 'CEO', 'status': 'complete', 'output': ceo_output})}\n\n"
    
    # Dev
    yield f"data: {json.dumps({'agent': 'Developer', 'status': 'working'})}\n\n"
    dev_output = await asyncio.to_thread(run_dev_agent, idea, ceo_output)
    yield f"data: {json.dumps({'agent': 'Developer', 'status': 'complete', 'output': dev_output})}\n\n"
    
    # Marketing and Finance run concurrently
    yield f"data: {json.dumps({'agent': 'Marketing', 'status': 'working'})}\n\n"
    yield f"data: {json.dumps({'agent': 'Finance', 'status': 'working'})}\n\n"
    
    marketing_task = wrap_task("Marketing", asyncio.to_thread(run_marketing_agent, idea, ceo_output))
    finance_task = wrap_task("Finance", asyncio.to_thread(run_finance_agent, idea, ceo_output, dev_output))
    
    for completed_task in asyncio.as_completed([marketing_task, finance_task]):
        name, result = await completed_task
        yield f"data: {json.dumps({'agent': name, 'status': 'complete', 'output': result})}\n\n"
        
    yield f"data: {json.dumps({'agent': 'System', 'status': 'done'})}\n\n"
