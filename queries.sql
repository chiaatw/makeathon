-- Given a finished goods Id, find all its raw materials which make it up
-- Example: Using Finished Good Id = 1
SELECT 
    rm.Id AS RawMaterial_Id,
    rm.SKU AS RawMaterial_SKU,
    c.Name AS Company,
    rm.Type AS Product_Type
FROM BOM b
JOIN BOM_Component bc ON b.Id = bc.BOMId
JOIN Product rm ON bc.ConsumedProductId = rm.Id
LEFT JOIN Company c ON rm.CompanyId = c.Id
WHERE b.ProducedProductId = 1; -- Replace 1 with your Finished Good Id

-- ---------------------------------------------------------------------
-- Given a raw material Id, find all finished goods (products) that use it
-- Example: Using Raw Material Id = 506
-- ---------------------------------------------------------------------
SELECT 
    fg.Id AS FinishedGood_Id,
    fg.SKU AS FinishedGood_SKU,
    c.Name AS Company,
    fg.Type AS Product_Type
FROM BOM_Component bc
JOIN BOM b ON bc.BOMId = b.Id
JOIN Product fg ON b.ProducedProductId = fg.Id
LEFT JOIN Company c ON fg.CompanyId = c.Id
WHERE bc.ConsumedProductId = 506; -- Replace 506 with your Raw Material Id

-- ---------------------------------------------------------------------
-- Given a raw material Id, find all the suppliers (producers) that offer it
-- Example: Using Raw Material Id = 506
-- ---------------------------------------------------------------------
SELECT 
    s.Id AS Supplier_Id,
    s.Name AS Supplier_Name
FROM Supplier_Product sp
JOIN Supplier s ON sp.SupplierId = s.Id
WHERE sp.ProductId = 506; -- Replace 506 with your Raw Material Id


