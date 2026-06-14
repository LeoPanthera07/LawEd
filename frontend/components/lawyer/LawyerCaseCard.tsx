import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { EscalationQueueItem } from "@/lib/types";

interface Props {
  item: EscalationQueueItem;
  onClick: () => void;
  isSelected: boolean;
}

export function LawyerCaseCard({ item, onClick, isSelected }: Props) {
  return (
    <Card
      className={`cursor-pointer transition-colors ${isSelected ? "border-amber-500 bg-amber-50 dark:bg-amber-950/20" : "hover:bg-muted/50"}`}
      onClick={onClick}
    >
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between">
          <CardTitle className="text-sm font-medium">
            {item.query_text.slice(0, 80)}
            {item.query_text.length > 80 ? "..." : ""}
          </CardTitle>
          <Badge
            variant={item.status === "pending" ? "destructive" : "secondary"}
          >
            {item.status}
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <p className="text-xs text-muted-foreground">
          Reason: {item.reason}
        </p>
        <p className="text-xs text-muted-foreground">
          {item.clauses.length} clauses &middot; Confidence:{" "}
          {Math.round(item.confidence_score * 100)}%
        </p>
        <p className="text-xs text-muted-foreground">
          {new Date(item.created_at).toLocaleDateString()}
        </p>
      </CardContent>
    </Card>
  );
}
