"use client";

import { useEffect, useState } from "react";

import { getSession, type SessionContract } from "@/features/auth/authClient";

import { fetchCourses, fetchLessons, LearningRequestError } from "./learningClient";
import { DashboardScreen } from "./DashboardScreen";
import type { DashboardModel, DashboardViewState } from "./dashboard.types";

interface BoundaryState { readonly state: DashboardViewState; readonly model: DashboardModel | null }

const initial: BoundaryState = { state: "loading", model: null };

function classify(error: unknown): DashboardViewState {
  if (!(error instanceof LearningRequestError)) return "recoverable-error";
  if (error.kind === "unauthenticated") return "unauthenticated";
  if (error.kind === "parent-not-found") return "parent-not-found";
  if (error.kind === "forbidden") return "forbidden";
  if (error.kind === "invalid-request") return "invalid-request";
  return "recoverable-error";
}

export function DashboardDataBoundary() {
  const [view, setView] = useState<BoundaryState>(initial);

  useEffect(() => {
    const controller = new AbortController();
    let generation = 0;
    let mounted = true;
    const isCurrent = (value: number) => mounted && value === generation && !controller.signal.aborted;

    void (async () => {
      try {
        const session: SessionContract | null = await getSession();
        const sessionGeneration = ++generation;
        if (!isCurrent(sessionGeneration)) return;
        if (session === null) { setView({ state: "unauthenticated", model: null }); return; }
        const courses = await fetchCourses({ signal: controller.signal });
        if (!isCurrent(sessionGeneration)) return;
        if (courses.length === 0) { setView({ state: "empty", model: { student: { displayName: session.user.username }, learning: { courses, lessons: [], selectedCourseId: null } } }); return; }
        const selectedCourseId = courses[0].id;
        const lessons = await fetchLessons(selectedCourseId, { signal: controller.signal });
        if (!isCurrent(sessionGeneration)) return;
        setView({ state: "ready", model: { student: { displayName: session.user.username }, learning: { courses, lessons, selectedCourseId } } });
      } catch (error) {
        if (!isCurrent(generation) || (error instanceof DOMException && error.name === "AbortError")) return;
        setView({ state: classify(error), model: null });
      }
    })();
    return () => { mounted = false; controller.abort(); generation += 1; };
  }, []);

  return view.model === null || view.state !== "ready"
    ? <DashboardScreen state={view.state} />
    : <DashboardScreen model={view.model} state="ready" />;
}
