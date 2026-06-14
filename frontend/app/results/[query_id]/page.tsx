"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useQueryPolling } from "@/hooks/useQuery";
import { usePayment } from "@/hooks/usePayment";
import { QueryProcessing } from "@/components/query/QueryProcessing";
import { ClauseMap } from "@/components/results/ClauseMap";
import { ConfidenceIndicator } from "@/components/results/ConfidenceIndicator";
import { Disclaimer } from "@/components/results/Disclaimer";
import { WriteupCTA } from "@/components/writeup/WriteupCTA";
import { PaymentModal } from "@/components/writeup/PaymentModal";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import api from "@/lib/api";
import type { APIResponse, GenerateWriteupRequest, GenerateWriteupResponse } from "@/lib/types";

export default function ResultsPage() {
  const params = useParams();
  const queryId = params.query_id as string;
  const { result, isPolling, error } = useQueryPolling(queryId);
  const { initiatePayment, isProcessing } = usePayment();
  const [showWriteupModal, setShowWriteupModal] = useState(false);
  const [writeupSubmitting, setWriteupSubmitting] = useState(false);

  if (error) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <Alert variant="destructive">
          <AlertTitle>Error</AlertTitle>
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (isPolling || !result) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <QueryProcessing />
      </div>
    );
  }

  if (result.status === "escalated") {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <Alert className="border-amber-200 bg-amber-50">
          <AlertTitle>Case Escalated for Expert Review</AlertTitle>
          <AlertDescription>
            Your query has been flagged for review by a legal expert.
            {result.escalation_reason && (
              <span className="block mt-1">
                Reason: {result.escalation_reason}
              </span>
            )}
            You will be notified when the review is complete.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  if (result.status === "failed") {
    return (
      <div className="mx-auto max-w-4xl px-4 py-12">
        <Alert variant="destructive">
          <AlertTitle>Analysis Failed</AlertTitle>
          <AlertDescription>
            We were unable to process your query. Please try again.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  const handleWriteupSubmit = async (data: GenerateWriteupRequest) => {
    setWriteupSubmitting(true);
    initiatePayment(
      { amount: 9900, payment_type: "writeup", query_id: queryId },
      async () => {
        try {
          const res = await api.post<APIResponse<GenerateWriteupResponse>>(
            "/writeup/generate",
            data
          );
          const writeup = res.data.data!;
          window.location.href = `/writeup/${writeup.writeup_id}`;
        } finally {
          setWriteupSubmitting(false);
          setShowWriteupModal(false);
        }
      }
    );
  };

  return (
    <div className="mx-auto max-w-4xl space-y-6 px-4 py-12">
      <div>
        <h1 className="text-2xl font-bold">Analysis Results</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Query: &ldquo;{result.input_text.slice(0, 100)}
          {result.input_text.length > 100 ? "..." : ""}&rdquo;
        </p>
        <div className="mt-2">
          <ConfidenceIndicator score={result.confidence_score} />
        </div>
      </div>

      {result.summary && (
        <div className="rounded-lg border bg-muted/50 p-4">
          <h3 className="mb-2 font-semibold">Summary</h3>
          <p className="text-sm">{result.summary}</p>
        </div>
      )}

      <ClauseMap clauses={result.clauses} />

      <WriteupCTA
        onProceed={() => setShowWriteupModal(true)}
        disabled={isProcessing}
      />

      <Disclaimer text={result.disclaimer} />

      <PaymentModal
        open={showWriteupModal}
        onOpenChange={setShowWriteupModal}
        queryId={queryId}
        onSubmit={handleWriteupSubmit}
        isSubmitting={writeupSubmitting}
      />
    </div>
  );
}
