"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import api from "@/lib/api";
import type {
  APIResponse,
  QuerySubmitRequest,
  QuerySubmitResponse,
  QueryResultResponse,
} from "@/lib/types";

export function useQuerySubmit() {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = useCallback(async (data: QuerySubmitRequest) => {
    setIsSubmitting(true);
    setError(null);
    try {
      const res = await api.post<APIResponse<QuerySubmitResponse>>(
        "/query/submit",
        data
      );
      return res.data.data!;
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { error?: { message?: string } } } })
          ?.response?.data?.error?.message || "Failed to submit query";
      setError(msg);
      throw err;
    } finally {
      setIsSubmitting(false);
    }
  }, []);

  return { submit, isSubmitting, error };
}

export function useQueryPolling(queryId: string | null) {
  const [result, setResult] = useState<QueryResultResponse | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const stopPolling = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsPolling(false);
  }, []);

  useEffect(() => {
    if (!queryId) return;
    setIsPolling(true);
    setError(null);

    const poll = async () => {
      try {
        const res = await api.get<APIResponse<QueryResultResponse>>(
          `/query/${queryId}`
        );
        const data = res.data.data!;
        setResult(data);
        if (
          data.status === "completed" ||
          data.status === "escalated" ||
          data.status === "failed"
        ) {
          stopPolling();
        }
      } catch (err: unknown) {
        const msg =
          (err as { response?: { data?: { error?: { message?: string } } } })
            ?.response?.data?.error?.message || "Failed to fetch result";
        setError(msg);
        stopPolling();
      }
    };

    poll();
    intervalRef.current = setInterval(poll, 2000);

    return () => stopPolling();
  }, [queryId, stopPolling]);

  return { result, isPolling, error };
}
