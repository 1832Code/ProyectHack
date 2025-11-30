"use client";

import { useState } from "react";
import { Lightbulb } from "lucide-react";
import { Button } from "@/components/ui/button";
import { OpportunityDrawer } from "@/components/opportunity-drawer";

export function OpportunityFloatingButton() {
  const [open, setOpen] = useState(false);

  return (
    <>
      <Button
        onClick={() => setOpen(true)}
        size="lg"
        className="fixed bottom-6 right-6 h-14 w-14 rounded-full shadow-lg hover:shadow-xl transition-shadow z-50"
      >
        <Lightbulb className="h-6 w-6" />
        <span className="sr-only">Open opportunity</span>
      </Button>
      <OpportunityDrawer open={open} onOpenChange={setOpen} />
    </>
  );
}
