"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import api from "@/lib/api";
import { useAuthStore } from "@/lib/auth";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import type { APIResponse } from "@/lib/types";

interface AdminStats {
  total_users: number;
  total_queries: number;
  total_escalations: number;
  total_payments: number;
  queries_today: number;
}

export default function AdminPage() {
  const user = useAuthStore((s) => s.user);
  const router = useRouter();
  const [stats, setStats] = useState<AdminStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== "admin") {
      router.push("/");
      return;
    }
  }, [user, router]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await api.get<APIResponse<AdminStats>>(
          "/admin/analytics"
        );
        setStats(res.data.data!);
      } catch {
        // silently fail
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (user?.role !== "admin") return null;

  return (
    <div className="mx-auto max-w-6xl px-4 py-12">
      <h1 className="mb-8 text-2xl font-bold">Admin Panel</h1>

      {loading ? (
        <LoadingSpinner className="py-12" />
      ) : (
        <Tabs defaultValue="overview">
          <TabsList>
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="users">Users</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
              <StatCard
                title="Total Users"
                value={stats?.total_users ?? 0}
              />
              <StatCard
                title="Total Queries"
                value={stats?.total_queries ?? 0}
              />
              <StatCard
                title="Queries Today"
                value={stats?.queries_today ?? 0}
              />
              <StatCard
                title="Escalations"
                value={stats?.total_escalations ?? 0}
              />
            </div>
          </TabsContent>

          <TabsContent value="users" className="mt-6">
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                User management coming soon.
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  );
}

function StatCard({ title, value }: { title: string; value: number }) {
  return (
    <Card>
      <CardHeader className="pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p className="text-3xl font-bold">{value.toLocaleString()}</p>
      </CardContent>
    </Card>
  );
}
