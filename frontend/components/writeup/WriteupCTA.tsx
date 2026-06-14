"use client";

import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface Props {
  onProceed: () => void;
  disabled?: boolean;
}

export function WriteupCTA({ onProceed, disabled }: Props) {
  return (
    <Card className="border-amber-200 bg-amber-50/50 dark:border-amber-900 dark:bg-amber-950/20">
      <CardHeader>
        <CardTitle className="text-lg">
          Generate a Formal Legal Writeup
        </CardTitle>
        <CardDescription>
          Get a professionally formatted complaint petition or legal notice based
          on the clauses identified above.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Button
          onClick={onProceed}
          disabled={disabled}
          className="bg-amber-600 hover:bg-amber-700"
        >
          Generate Writeup (Paid)
        </Button>
      </CardContent>
    </Card>
  );
}
