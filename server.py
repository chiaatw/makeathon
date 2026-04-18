from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
from workflow_orchestrator import extract_supply_chain, fetch_fg_compliance, fetch_rm_compliance, get_db_connection
import asyncio
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AnalyzeRequest(BaseModel):
    company: str
    product_sku: str

@app.get("/api/products")
async def get_products(company: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT p.SKU 
        FROM Product p 
        JOIN Company c ON p.CompanyId = c.Id 
        WHERE c.Name = ? AND p.Type = 'finished-good'
    """, (company,))
    products = [row[0] for row in cursor.fetchall()]
    conn.close()
    return {"products": products}

@app.post("/api/analyze")
async def analyze(req: AnalyzeRequest):
    print(f"Analyzing {req.company} {req.product_sku}")
    fgs, rm_suppliers_map = extract_supply_chain([req.company], req.product_sku)
    
    target_fgs = [fg for fg in fgs if req.product_sku in (fg['sku'], fg['canonical_name'])]
    
    if not target_fgs:
         return {"error": f"Product SKU {req.product_sku} not found for {req.company}"}
         
    fg = target_fgs[0]
    
    # We pass the full fg object to fetch_fg_compliance
    fg_task = asyncio.create_task(fetch_fg_compliance(fg))
    
    rm_tasks = []
    
    for rm_id, rm_data in rm_suppliers_map.items():
        rm_tasks.append(asyncio.create_task(fetch_rm_compliance(rm_id, rm_data)))
             
    fg_res = await fg_task
    rm_res = await asyncio.gather(*rm_tasks)
    
    out = {
       "finished_goods_compliance": fg_res[1] if fg_res and len(fg_res) > 1 else {},
       "raw_materials_comparison": []
    }
    
    for rm in rm_res:
         if rm and len(rm) > 1: out["raw_materials_comparison"].append(rm[1])
         
    return out

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

