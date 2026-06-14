import { ScrollArea } from "@/components/ui/scroll-area";
import { LawyerCaseCard } from "./LawyerCaseCard";
import type { EscalationQueueItem } from "@/lib/types";

interface Props {
  items: EscalationQueueItem[];
  selectedId: string | null;
  onSelect: (id: string) => void;
}

export function CaseQueue({ items, selectedId, onSelect }: Props) {
  if (items.length === 0) {
    return (
      <p className="py-8 text-center text-muted-foreground">
        No pending escalations. Check back later.
      </p>
    );
  }

  return (
    <ScrollArea className="h-[calc(100vh-200px)]">
      <div className="space-y-2 pr-4">
        {items.map((item) => (
          <LawyerCaseCard
            key={item.escalation_id}
            item={item}
            isSelected={selectedId === item.escalation_id}
            onClick={() => onSelect(item.escalation_id)}
          />
        ))}
      </div>
    </ScrollArea>
  );
}
