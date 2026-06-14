import { Badge } from "@/components/ui/badge";

interface Props {
  score: number;
}

export function ConfidenceIndicator({ score }: Props) {
  const pct = Math.round(score * 100);
  const variant =
    score >= 0.7 ? "default" : score >= 0.45 ? "secondary" : "destructive";
  const label =
    score >= 0.7 ? "High Confidence" : score >= 0.45 ? "Moderate" : "Low";

  return (
    <div className="flex items-center gap-2">
      <div className="h-2 w-24 overflow-hidden rounded-full bg-muted">
        <div
          className={`h-full rounded-full transition-all ${
            score >= 0.7
              ? "bg-green-500"
              : score >= 0.45
                ? "bg-amber-500"
                : "bg-red-500"
          }`}
          style={{ width: `${pct}%` }}
        />
      </div>
      <Badge variant={variant}>
        {label} ({pct}%)
      </Badge>
    </div>
  );
}
