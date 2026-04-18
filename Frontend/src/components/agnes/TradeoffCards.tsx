import { Card } from "@/components/ui/card";
import { cn } from "@/lib/utils";
import { CheckCircle2, Factory, Package } from "lucide-react";

export const TradeoffCards = ({ backendData }: { backendData?: any }) => {
  if (!backendData) return null;

  const fgs = backendData.finished_goods_compliance || {};
  let rms = backendData.raw_materials_comparison || [];

  // Parse JSON strings to objects if they are strings
  let parsedRms: any[] = [];
  try {
    parsedRms = rms.map((rm: any) =>
      typeof rm === "string" ? JSON.parse(rm) : rm,
    );
  } catch (e) {
    console.error("Error parsing rms", e);
  }

  let parsedFg: any = {};
  try {
    parsedFg = typeof fgs === "string" ? JSON.parse(fgs) : fgs;
  } catch (e) {
    console.error("Error parsing fg", e);
  }

  return (
    <Card className="p-6 shadow-elegant border-border/70 bg-card">
      <div className="flex items-center justify-between mb-5">
        <h3 className="text-lg font-semibold tracking-tight">
          Supply Chain AI Compliance Analysis
        </h3>
      </div>

      <div className="space-y-6">
        {/* Finished Good Section */}
        <div className="rounded-xl border border-primary/20 bg-primary/5 p-5">
          <div className="flex items-center gap-3 mb-4">
            <Package className="w-5 h-5 text-primary" />
            <div className="font-semibold text-primary-foreground text-md">
              Required Direct Compliance for{" "}
              {parsedFg.product_sku || "Main Product"}
            </div>
          </div>
          <ul className="list-disc list-inside space-y-1 ml-4 text-sm text-foreground">
            {(parsedFg.required_compliance || []).map(
              (req: string, i: number) => (
                <li key={i}>{req}</li>
              ),
            )}
            {!(parsedFg.required_compliance || []).length && (
              <span className="text-muted-foreground">
                No specific compliance requirements discovered.
              </span>
            )}
          </ul>
        </div>

        {/* Raw Materials / Suppliers Section */}
        <div className="space-y-4">
          <h4 className="text-md font-semibold font-medium text-foreground">
            Available Suppliers & Fulfillments
          </h4>
          {parsedRms.map((rmItem: any, idx: number) => {
            // Sort suppliers by amount of fulfilled compliance requirements
            const suppliers = (rmItem.supplier_comparison || []).sort(
              (a: any, b: any) =>
                (b.fulfilled_compliance?.length || 0) -
                (a.fulfilled_compliance?.length || 0),
            );

            return (
              <div
                key={idx}
                className="border border-border/60 rounded-xl p-5 bg-card shadow-sm"
              >
                <div className="text-sm uppercase tracking-wide font-bold text-muted-foreground mb-3">
                  Raw Material: {rmItem.raw_material_sku || "Unknown"}
                </div>
                        <div className="grid grid-cols-2 gap-4">
                  {suppliers.map((s: any, sIdx: number) => {
                    const matchCount = (s.fulfilled_compliance || []).length;
                    const isMatched = matchCount > 0;
                    
                    return (
                      <div
                        key={sIdx}
                        className={`rounded-lg bg-secondary/30 border p-4 ${isMatched ? "border-success/50 bg-success/5 shadow-sm" : "border-destructive/30 opacity-70"}`}
                      >
                        <div className="flex items-center gap-2 mb-2">
                          <Factory className={`w-4 h-4 ${isMatched ? "text-success" : "text-muted-foreground"}`} />
                          <span className={`font-semibold ${isMatched ? "text-success-foreground" : "text-foreground"}`}>
                            {s.supplier}
                          </span>
                        </div>
                        <div className="text-xs text-muted-foreground mb-2">
                          Verified Compliance:
                        </div>
                        <ul className="space-y-1.5 list-none">
                          {(s.fulfilled_compliance || []).map(
                            (fc: string, fcIdx: number) => (
                              <li
                                key={fcIdx}
                                className="flex gap-2 text-xs items-start"
                              >
                                <CheckCircle2 className="w-3.5 h-3.5 text-success shrink-0 mt-0.5" />
                                <span className="text-foreground">{fc}</span>
                              </li>
                            ),
                          )}
                          {!isMatched && (
                            <span className="text-xs text-destructive/80 italic font-medium">
                              Does not explicitly fulfill constraints.
                            </span>
                          )}
                        </ul>
                      </div>
                    );
                  })}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Card>
  );
};
