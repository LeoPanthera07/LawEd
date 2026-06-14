"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { CaseQueue } from "@/components/lawyer/CaseQueue";
import { CaseReviewPanel } from "@/components/lawyer/CaseReviewPanel";
import type {
  APIResponse,
  EscalationQueueItem,
  EscalationQueueResponse,
  ReviewEscalationRequest,
} from "@/lib/types";

export default function LawyerPage() {
  const user = useAuthStore((s) => s.user);
  const router = useRouter();
  const [items, setItems] = useState<EscalationQueueItem[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reviewedToday, setReviewedToday] = useState(0);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (user?.role !== "lawyer") {
      router.push("/");
      return;
    }
  }, [user, router]);

  const fetchQueue = useCallback(async () => {
    try {
      const res = await api.get<APIResponse<EscalationQueueResponse>>(
        "/escalations/"
      );
      const data = res.data.data!;
      setItems(data.items);
      setReviewedToday(data.reviewed_today);
    } catch {
      // silently fail
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchQueue();
  }, [fetchQueue]);

  const selectedItem = items.find((i) => i.escalation_id === selectedId);

  const handleReview = async (data: ReviewEscalationRequest) => {
    if (!selectedId) return;
    setSubmitting(true);
    try {
      await api.put(`/escalations/${selectedId}/review`, data);
      setSelectedId(null);
      await fetchQueue();
    } finally {
      setSubmitting(false);
    }
  };

  if (user?.role !== "lawyer") return null;

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">Lawyer Review Dashboard</h1>
        <p className="text-muted-foreground">
          {items.length} pending escalations &middot; {reviewedToday} reviewed
          today
        </p>
      </div>

      {loading ? (
        <LoadingSpinner className="py-12" />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[350px_1fr]">
          <CaseQueue
            items={items}
            selectedId={selectedId}
            onSelect={setSelectedId}
          />
          <div>
            {selectedItem ? (
              <CaseReviewPanel
                item={selectedItem}
                onSubmitReview={handleReview}
                isSubmitting={submitting}
              />
            ) : (
              <div className="flex h-full items-center justify-center text-muted-foreground">
                Select a case from the queue to review
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
