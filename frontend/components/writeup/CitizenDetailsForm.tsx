"use client";

import { useState } from "react";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import type { GenerateWriteupRequest } from "@/lib/types";

interface Props {
  queryId: string;
  onSubmit: (data: GenerateWriteupRequest) => void;
  isSubmitting: boolean;
}

export function CitizenDetailsForm({ queryId, onSubmit, isSubmitting }: Props) {
  const [form, setForm] = useState({
    citizen_name: "",
    citizen_address: "",
    incident_date: "",
    incident_description: "",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit({ ...form, query_id: queryId });
  };

  const update = (field: string, value: string) =>
    setForm((prev) => ({ ...prev, [field]: value }));

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="citizen_name">Full Name</Label>
          <Input
            id="citizen_name"
            required
            value={form.citizen_name}
            onChange={(e) => update("citizen_name", e.target.value)}
          />
        </div>
        <div className="space-y-2">
          <Label htmlFor="incident_date">Incident Date</Label>
          <Input
            id="incident_date"
            type="date"
            required
            value={form.incident_date}
            onChange={(e) => update("incident_date", e.target.value)}
          />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor="citizen_address">Address</Label>
        <Input
          id="citizen_address"
          required
          value={form.citizen_address}
          onChange={(e) => update("citizen_address", e.target.value)}
        />
      </div>
      <div className="space-y-2">
        <Label htmlFor="incident_description">
          Brief description of the incident
        </Label>
        <Textarea
          id="incident_description"
          required
          className="min-h-[100px]"
          value={form.incident_description}
          onChange={(e) => update("incident_description", e.target.value)}
        />
      </div>
      <Button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-amber-600 hover:bg-amber-700"
      >
        {isSubmitting ? "Processing..." : "Proceed to Payment"}
      </Button>
    </form>
  );
}
