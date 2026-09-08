"use client";

import React from "react";
import { useParams } from "next/navigation";
import { CohortOrchestrationScreen } from "@/components/supervision/CohortOrchestrationScreen";

export default function MentorCohortSupervisionPage() {
  const params = useParams();
  const cohortId = typeof params?.cohortId === "string" ? params.cohortId : "c0000000-0000-0000-0000-000000000001";
  const mentorId = "m0000000-0000-0000-0000-000000000001";

  return (
    <main style={{ maxWidth: "1200px", margin: "0 auto", padding: "1.5rem" }}>
      <CohortOrchestrationScreen cohortId={cohortId} mentorId={mentorId} />
    </main>
  );
}
