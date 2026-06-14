"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { CitizenDetailsForm } from "./CitizenDetailsForm";
import type { GenerateWriteupRequest } from "@/lib/types";

interface Props {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  queryId: string;
  onSubmit: (data: GenerateWriteupRequest) => void;
  isSubmitting: boolean;
}

export function PaymentModal({
  open,
  onOpenChange,
  queryId,
  onSubmit,
  isSubmitting,
}: Props) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Generate Legal Writeup</DialogTitle>
          <DialogDescription>
            Provide your details below. After payment, a formal legal document
            will be generated and available for download.
          </DialogDescription>
        </DialogHeader>
        <CitizenDetailsForm
          queryId={queryId}
          onSubmit={onSubmit}
          isSubmitting={isSubmitting}
        />
      </DialogContent>
    </Dialog>
  );
}
