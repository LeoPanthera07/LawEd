"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { ClauseResult } from "@/lib/types";

interface Props {
  clause: ClauseResult;
}

export function ClauseCard({ clause }: Props) {
  const [expanded, setExpanded] = useState(false);
  const relevancePct = Math.round(clause.relevance_score * 100);

  return (
    <Card
      className="cursor-pointer transition-shadow hover:shadow-md"
      onClick={() => setExpanded(!expanded)}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-base">
            {clause.act} — Section {clause.section_number}
          </CardTitle>
          <Badge
            variant={relevancePct >= 70 ? "default" : "secondary"}
            className="ml-2 shrink-0"
          >
            {relevancePct}% relevant
          </Badge>
        </div>
        {clause.section_title && (
          <p className="text-sm text-muted-foreground">
            {clause.section_title}
          </p>
        )}
      </CardHeader>
      <CardContent>
        <p className="text-sm">{clause.plain_language}</p>
        {expanded && (
          <div className="mt-3 rounded-md bg-muted p-3">
            <p className="text-xs font-medium text-muted-foreground">
              Original statute text:
            </p>
            <p className="mt-1 text-sm italic">{clause.text_excerpt}</p>
          </div>
        )}
        <p className="mt-2 text-xs text-muted-foreground">
          {expanded ? "Click to collapse" : "Click to see original text"}
        </p>
      </CardContent>
    </Card>
  );
}
