"use client";

import { LoadingSpinner } from "@/components/shared/LoadingSpinner";

const STEPS = [
  "Validating your input",
  "Detecting language",
  "Expanding legal queries",
  "Searching statute database",
  "Traversing legal graph",
  "Merging results",
  "Evaluating confidence",
  "Synthesizing response",
];

export function QueryProcessing() {
  return (
    <div className="flex flex-col items-center gap-6 py-12">
      <LoadingSpinner className="mb-2" />
      <h2 className="text-xl font-semibold">Analyzing your case...</h2>
      <div className="w-full max-w-sm space-y-2">
        {STEPS.map((step, i) => (
          <div key={i} className="flex items-center gap-3 text-sm text-muted-foreground">
            <div className="h-2 w-2 animate-pulse rounded-full bg-amber-500" />
            {step}
          </div>
        ))}
      </div>
      <p className="text-xs text-muted-foreground">
        This usually takes 10-15 seconds
      </p>
    </div>
  );
}
