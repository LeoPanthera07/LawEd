"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { useQuerySubmit } from "@/hooks/useQuery";
import { useAuthStore } from "@/lib/auth";

export function QueryInput() {
  const [queryText, setQueryText] = useState("");
  const { submit, isSubmitting, error } = useQuerySubmit();
  const router = useRouter();
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);

  const handleSubmit = async () => {
    if (!queryText.trim()) return;
    if (!isAuthenticated) {
      router.push("/login");
      return;
    }
    try {
      const result = await submit({ query_text: queryText.trim() });
      router.push(`/results/${result.query_id}`);
    } catch {
      // error state is set by the hook
    }
  };

  return (
    <div className="mx-auto w-full max-w-2xl space-y-4">
      <Textarea
        placeholder="Describe your legal situation in plain language... (Hindi, English, or Hinglish)"
        value={queryText}
        onChange={(e) => setQueryText(e.target.value)}
        className="min-h-[120px] resize-none text-base"
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) handleSubmit();
        }}
      />
      {error && <p className="text-sm text-destructive">{error}</p>}
      <div className="flex items-center justify-between">
        <p className="text-xs text-muted-foreground">
          Press Ctrl+Enter to submit
        </p>
        <Button
          onClick={handleSubmit}
          disabled={isSubmitting || !queryText.trim()}
          className="bg-amber-600 hover:bg-amber-700"
        >
          {isSubmitting ? "Analyzing..." : "Get Legal Intelligence"}
        </Button>
      </div>
    </div>
  );
}
