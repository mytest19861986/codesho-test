"use client";

import { useEffect, useState } from "react";

import { getSession, type SessionContract } from "@/features/auth/authClient";

import { DashboardScreen } from "./DashboardScreen";
import { dashboardFixture } from "./dashboard.fixture";
import type { DashboardModel } from "./dashboard.types";

function modelForSession(session: SessionContract): DashboardModel {
  return {
    ...dashboardFixture,
    student: { ...dashboardFixture.student, displayName: session.user.username },
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
