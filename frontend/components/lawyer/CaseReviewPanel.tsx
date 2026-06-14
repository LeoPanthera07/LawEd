"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ClauseMap } from "@/components/results/ClauseMap";
import { ConfidenceIndicator } from "@/components/results/ConfidenceIndicator";
import type { EscalationQueueItem, ReviewEscalationRequest } from "@/lib/types";

interface Props {
  item: EscalationQueueItem;
  onSubmitReview: (data: ReviewEscalationRequest) => Promise<void>;
  isSubmitting: boolean;
}

export function CaseReviewPanel({ item, onSubmitReview, isSubmitting }: Props) {
  const [resolution, setResolution] = useState("");
  const [notes, setNotes] = useState("");
  const [approved, setApproved] = useState(false);

  const handleSubmit = async () => {
    await onSubmitReview({
      resolution,
      lawyer_notes: notes,
      approved_for_writeup: approved,
    });
  };

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Query</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm">{item.query_text}</p>
          <div className="mt-2">
            <ConfidenceIndicator score={item.confidence_score} />
          </div>
          <p className="mt-2 text-xs text-muted-foreground">
            Escalation reason: {item.reason}
          </p>
        </CardContent>
      </Card>

      <ClauseMap clauses={item.clauses} />

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Your Review</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Resolution</Label>
            <Textarea
              value={resolution}
              onChange={(e) => setResolution(e.target.value)}
              placeholder="Describe your resolution or corrections..."
              className="min-h-[80px]"
            />
          </div>
          <div className="space-y-2">
            <Label>Notes</Label>
            <Textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Additional notes..."
            />
          </div>
          <label className="flex items-center gap-2 text-sm">
            <input
              type="checkbox"
              checked={approved}
              onChange={(e) => setApproved(e.target.checked)}
              className="rounded"
            />
            Approve for writeup generation
          </label>
          <Button
            onClick={handleSubmit}
            disabled={isSubmitting || !resolution.trim()}
            className="w-full bg-amber-600 hover:bg-amber-700"
          >
            {isSubmitting ? "Submitting..." : "Submit Review"}
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
