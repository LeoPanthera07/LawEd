"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { APIResponse, QueryStatus } from "@/lib/types";

interface CaseHistoryItem {
  query_id: string;
  input_text: string;
  status: QueryStatus;
  created_at: string;
  clause_count: number;
}

interface CaseHistoryResponse {
  items: CaseHistoryItem[];
  total: number;
}

const STATUS_COLORS: Record<QueryStatus, string> = {
  pending: "secondary",
  processing: "secondary",
  completed: "default",
  escalated: "destructive",
  failed: "destructive",
};

export default function DashboardPage() {
  const user = useAuthStore((s) => s.user);
  const [cases, setCases] = useState<CaseHistoryItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchCases = async () => {
      try {
        const res = await api.get<APIResponse<CaseHistoryResponse>>(
          "/query/history"
        );
        setCases(res.data.data?.items || []);
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    };
    fetchCases();
  }, []);

  return (
    <div className="mx-auto max-w-4xl px-4 py-12">
      <div className="mb-8">
        <h1 className="text-2xl font-bold">My Cases</h1>
        <p className="text-muted-foreground">
          Welcome back, {user?.full_name || "User"}.{" "}
          {user && `${3 - user.free_queries_used} free queries remaining.`}
        </p>
      </div>

      {loading ? (
        <LoadingSpinner className="py-12" />
      ) : cases.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <p className="text-muted-foreground">
              No cases yet.{" "}
              <Link href="/" className="text-amber-600 hover:underline">
                Submit your first query
              </Link>
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {cases.map((c) => (
            <Link key={c.query_id} href={`/results/${c.query_id}`}>
              <Card className="cursor-pointer transition-shadow hover:shadow-md">
                <CardHeader className="pb-2">
                  <div className="flex items-start justify-between">
                    <CardTitle className="text-base font-medium">
                      {c.input_text.slice(0, 100)}
                      {c.input_text.length > 100 ? "..." : ""}
                    </CardTitle>
                    <Badge
                      variant={
                        STATUS_COLORS[c.status] as
                          | "default"
                          | "secondary"
                          | "destructive"
                      }
                    >
                      {c.status}
                    </Badge>
                  </div>
                </CardHeader>
                <CardContent className="pt-0">
                  <p className="text-xs text-muted-foreground">
                    {new Date(c.created_at).toLocaleDateString()} &middot;{" "}
                    {c.clause_count} clauses found
                  </p>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
