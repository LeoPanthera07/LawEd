"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import api from "@/lib/api";
import { LoadingSpinner } from "@/components/shared/LoadingSpinner";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";
import type { APIResponse } from "@/lib/types";

interface WriteupData {
  writeup_id: string;
  status: string;
  pdf_url: string;
}

export default function WriteupPage() {
  const params = useParams();
  const writeupId = params.writeup_id as string;
  const [writeup, setWriteup] = useState<WriteupData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWriteup = async () => {
      try {
        const res = await api.get<APIResponse<WriteupData>>(
          `/writeup/${writeupId}`
        );
        setWriteup(res.data.data!);
      } catch {
        setError("Failed to load writeup");
      } finally {
        setLoading(false);
      }
    };
    fetchWriteup();
  }, [writeupId]);

  if (loading) return <LoadingSpinner className="py-20" />;

  if (error) {
    return (
      <div className="mx-auto max-w-2xl px-4 py-12">
        <Alert variant="destructive">
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl px-4 py-12">
      <Card>
        <CardHeader>
          <CardTitle>Legal Writeup Ready</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            Your formal legal document has been generated and is ready for
            download.
          </p>
          {writeup?.pdf_url ? (
            <Button asChild className="bg-amber-600 hover:bg-amber-700">
              <a href={writeup.pdf_url} target="_blank" rel="noopener noreferrer">
                Download PDF
              </a>
            </Button>
          ) : (
            <p className="text-sm text-muted-foreground">
              Status: {writeup?.status || "Processing..."}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
