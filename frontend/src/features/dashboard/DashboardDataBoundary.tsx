"use client";

import { useEffect, useState } from "react";

import { getSession, type SessionContract } from "@/features/auth/authClient";

import { DashboardScreen } from "./DashboardScreen";
import type { DashboardModel } from "./dashboard.types";

function modelForSession(session: SessionContract): DashboardModel {
  return {
    student: { displayName: session.user.username, greeting: "Dashboard connected", className: `Tenant: ${session.tenant.slug}` },
    learning: { course: "Not connected", module: "Not connected", lesson: "Not connected", progress: 0, totalUnits: 0, completedUnits: 0 },
    nextSession: { title: "Not connected", date: "Not available", time: "Not available", type: "Read-only placeholder", status: "Unavailable" },
    momentum: { xp: 0, rank: "Not connected", streak: 0 },
    assignment: { title: "Not connected", dueLabel: "Not available", status: "Unavailable", actionLabel: "Unavailable" },
    recommendation: { title: "Not connected", reason: "Learning data will appear when the reviewed contract is available." },
    attention: ["Academic dashboard data is not connected yet."],
  };
}

export function DashboardDataBoundary() {
  const [model, setModel] = useState<DashboardModel | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    let active = true;
    void getSession().then((session) => {
      if (!active) return;
      if (session === null) setFailed(true);
      else setModel(modelForSession(session));
    });
    return () => { active = false; };
  }, []);

  if (failed) return <DashboardScreen state="error" />;
  if (model === null) return <DashboardScreen state="loading" />;
  return <DashboardScreen model={model} />;
}
