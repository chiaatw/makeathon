import asyncio
import sqlite3
import json
from req_gatherer import producer_app, supplier_app

producer_app.set_up()
supplier_app.set_up()

def get_db_connection():
    return sqlite3.connect('db/db.sqlite')

def extract_supply_chain(company_names, product_sku=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    placeholders = ",".join(["?"] * len(company_names))
    
    query_fgs_safe = f"""
        SELECT DISTINCT p.Id, p.SKU, c.Name as CompanyName, p.canonical_material_name
        FROM Product p
        JOIN Company c ON p.CompanyId = c.Id
        JOIN BOM b ON p.Id = b.ProducedProductId
        WHERE c.Name IN ({placeholders})
    """
    if product_sku:
        query_fgs_safe += " AND p.SKU = ?"
        cursor.execute(query_fgs_safe, [*company_names, product_sku])
    else:
        cursor.execute(query_fgs_safe, company_names)
        
    fgs = cursor.fetchall()
    
    unique_fgs = []
    if not fgs:
        return [], {}
        
    fg_ids = tuple([fg[0] for fg in fgs])
    
    for fg in fgs:
        unique_fgs.append({
            "id": fg[0],
            "sku": fg[1],
            "company": fg[2],
            "canonical_name": fg[3] if len(fg) > 3 else fg[1]
        })
    
    fg_placeholders = ",".join(["?"] * len(fg_ids))
    query_rms = f"""
        SELECT DISTINCT 
            rm.Id AS RawMaterial_Id,
            rm.SKU AS RawMaterial_SKU,
            rm.canonical_material_name
        FROM BOM b
        JOIN BOM_Component bc ON b.Id = bc.BOMId
        JOIN Product rm ON bc.ConsumedProductId = rm.Id
        WHERE b.ProducedProductId IN ({fg_placeholders})
    """
    cursor.execute(query_rms, fg_ids)
    rms = cursor.fetchall()
    
    rm_suppliers_map = {}
    for rm in rms:
        rm_id = rm[0]
        query_suppliers = "SELECT s.Name FROM Supplier_Product sp JOIN Supplier s ON sp.SupplierId = s.Id WHERE sp.ProductId = ?"
        cursor.execute(query_suppliers, (rm_id,))
        suppliers = [r[0] for r in cursor.fetchall()]
        
        rm_suppliers_map[rm_id] = {
            "sku": rm[1],
            "name": rm[2] if len(rm) > 2 else rm[1],
            "suppliers": suppliers
        }
        
    conn.close()
    return unique_fgs, rm_suppliers_map

async def run_query(app, prompt, user_id):
    chunks = []
    async for event in app.async_stream_query(message=prompt, user_id=user_id):
        # We only want to extract the final text output of the model
        if isinstance(event, dict):
            content = event.get("content")
            if isinstance(content, dict):
                parts = content.get("parts", [])
                for part in parts:
                    if "text" in part:
                        chunks.append(part["text"])
                    elif "function_call" in part:
                        # You could log function calls here, but we don't append them to the text chunks
                        pass
            elif isinstance(content, str) and content:
                chunks.append(content)
        elif isinstance(event, str):
            chunks.append(event)
    
    if chunks:
        # Just grab the last chunk which typically contains the finalized model response
        res = chunks[-1].strip()
        if res.startswith("```json"):
            res = res[7:]
        if res.startswith("```"):
            res = res[3:]
        if res.endswith("```"):
            res = res[:-3]
        return res.strip()
    return ""

async def fetch_fg_compliance(fg, certifications=[]):
    cert_text = ""
    if certifications:
        cert_text = f" This product must strictly comply with the following certifications: {', '.join(certifications)}. "
    
    prompt = (
        f"Research the compliance requirements for the finished product manufactured by '{fg['company']}'. "
        f"The product SKU/Name is '{fg['sku']}' (canonical name: '{fg['canonical_name']}')."
        f"{cert_text}"
        f"Output ONLY a raw JSON strictly formatted as follows, without markdown tags: "
        f"{{ \"product_sku\": \"{fg['sku']}\", \"required_compliance\": [\"list of requirements\"] }}"
    )
    res = await run_query(producer_app.app, prompt, f"fg_{fg['id']}")
    return fg['id'], res

async def fetch_rm_compliance(rm_id, rm_data):
    suppliers_list = ", ".join(rm_data['suppliers']) if rm_data['suppliers'] else "Unknown suppliers"
    prompt = (
        f"Research the raw material '{rm_data['sku']}' (canonical name: '{rm_data['name']}'). "
        f"For EACH of the following potential suppliers: {suppliers_list}, actively search their SPECIFIC company website "
        f"for this EXACT raw material. Extract the actual compliance standards (e.g., certifications, FDA, EFSA, GMP) "
        f"they explicitly state for this raw material. "
        f"Only consider these exact suppliers. Do not look for others. Do not invent standards. "
        f"Output ONLY a raw JSON strictly formatted as follows, without markdown tags: "
        f"{{ \"raw_material_sku\": \"{rm_data['sku']}\", \"supplier_comparison\": [ "
        f"{{ \"supplier\": \"name\", \"fulfilled_compliance\": [\"list of standards found on their site\"] }} ] }}"
    )
    res = await run_query(supplier_app.app, prompt, f"rm_{rm_id}")
    return rm_id, res

async def main():
    test_companies = ['Thrive Market']
    print(f"Extracting supply chain for {test_companies}...")
    fgs, rm_suppliers_map = extract_supply_chain(test_companies)
    
    # We constrain the list for testing
    fgs = fgs[:1]
    rm_suppliers_map = dict(list(rm_suppliers_map.items())[:1])
    
    print(f"Found {len(fgs)} Finished Good(s) and {len(rm_suppliers_map)} Raw Material(s) limited.")
    
    # Limit concurrency to 2 parallel tasks to avoid RESOURCE_EXHAUSTED errors
    sem = asyncio.Semaphore(2)
    
    async def bound_fetch_fg(fg):
        async with sem:
            return await fetch_fg_compliance(fg)

    async def bound_fetch_rm(rm_id, data):
        async with sem:
            return await fetch_rm_compliance(rm_id, data)

    fg_tasks = [bound_fetch_fg(fg) for fg in fgs]
    rm_tasks = [bound_fetch_rm(rm_id, data) for rm_id, data in rm_suppliers_map.items()]

    fg_results = await asyncio.gather(*fg_tasks)
    rm_results = await asyncio.gather(*rm_tasks)
    
    fg_final = []
    for fg_id, res in fg_results:
        try:
            print("RAW FG:", repr(res))
            clean_res = res.strip().removeprefix("```json").removesuffix("```").strip()
            fg_final.append(json.loads(clean_res))
        except:
            fg_final.append({"error": "unparseable", "raw": res})
            
    rm_final = []
    for rm_id, res in rm_results:
        try:
            print("RAW RM:", repr(res))
            clean_res = res.strip().removeprefix("```json").removesuffix("```").strip()
            rm_final.append(json.loads(clean_res))
        except:
            rm_final.append({"error": "unparseable", "raw": res})
            
    final_output = {
        "finished_goods_compliance": fg_final,
        "raw_materials_comparison": rm_final
    }
    
    print("\n\n=============== FINAL JSON REPORT ===============\n")
    print(json.dumps(final_output, indent=2))

if __name__ == "__main__":
    asyncio.run(main())