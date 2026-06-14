import type { ClauseResult } from "@/lib/types";
import { ClauseCard } from "./ClauseCard";

interface Props {
  clauses: ClauseResult[];
}

export function ClauseMap({ clauses }: Props) {
  if (clauses.length === 0) {
    return (
      <p className="py-8 text-center text-muted-foreground">
        No relevant clauses found.
      </p>
    );
  }

  return (
    <div className="space-y-3">
      <h3 className="text-lg font-semibold">
        Relevant Clauses ({clauses.length})
      </h3>
      {clauses.map((clause, i) => (
        <ClauseCard key={`${clause.act}-${clause.section_number}-${i}`} clause={clause} />
      ))}
    </div>
  );
}
