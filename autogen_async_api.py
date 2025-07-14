from fastapi import FastAPI, Request, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uuid
import asyncio
import time
import os
from typing import Dict

app = FastAPI(title="AutoGen Async API", version="1.0.0")

# 定义请求模型
class QueryRequest(BaseModel):
    query: str

# 简单内存缓存任务结果
TASK_RESULTS: Dict[str, Dict] = {}

# 健康检查端点
@app.get("/")
async def root():
    return {"message": "AutoGen Async API is running", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

# 模拟 AutoGen 多 Agent 分析逻辑
async def run_autogen_async(query: str, task_id: str):
    print(f"[AutoGen] Running task {task_id} for query: {query}")
    await asyncio.sleep(10)  # 模拟长时间任务

    # 生成假结果
    result = {
        "answer": f"关于 '{query}' 的分析结果如下：水果类商品销量最高。",
        "table": {
            "columns": ["类目", "销量"],
            "rows": [["水果", 18320], ["服饰", 13200], ["母婴", 12800]]
        },
        "chart": {
            "title": "销量前3类目",
            "type": "bar",
            "xAxis": ["水果", "服饰", "母婴"],
            "series": [18320, 13200, 12800]
        }
    }

    TASK_RESULTS[task_id] = result
    print(f"[AutoGen] Task {task_id} completed")

# 用户调用插件接口：发起分析任务
@app.post("/coze-plugin/query")
async def handle_query(request_data: QueryRequest, background_tasks: BackgroundTasks):
    query = request_data.query
    task_id = str(uuid.uuid4())

    # 异步处理任务
    background_tasks.add_task(run_autogen_async, query, task_id)

    return JSONResponse({
        "status": "processing",
        "task_id": task_id,
        "estimated_time": "10s"
    })

# 用户轮询查看分析结果
@app.get("/coze-plugin/result/{task_id}")
async def get_result(task_id: str):
    result = TASK_RESULTS.get(task_id)
    if result:
        return JSONResponse({"status": "completed", "result": result})
    else:
        return JSONResponse({"status": "processing"})

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)