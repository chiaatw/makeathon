import { useState } from "react";
import { AppHeader } from "@/components/agnes/AppHeader";
import { InputScreen } from "@/components/agnes/InputScreen";
import { AnalysisScreen } from "@/components/agnes/AnalysisScreen";
import { DEFAULT_CASE, SourcingCase } from "@/lib/agnes-data";

const Index = () => {
  const [view, setView] = useState<"input" | "analysis">("input");
  const [data, setData] = useState<SourcingCase>(DEFAULT_CASE);

  return (
    <div className="min-h-screen bg-gradient-surface">
      <AppHeader />
      <main>
        {view === "input" ? (
          <InputScreen data={data} setData={setData} onRun={() => setView("analysis")} />
        ) : (
          <AnalysisScreen
            data={data}
            onBack={() => setView("input")}
            onAnother={() => setView("input")}
          />
        )}
      </main>
      <footer className="border-t border-border/60 py-6 mt-12">
        <div className="max-w-7xl mx-auto px-8 flex items-center justify-between text-xs text-muted-foreground">
          <div>Agnes · AI Sourcing Decision Support</div>
          <div>Demo build · mock data only</div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
