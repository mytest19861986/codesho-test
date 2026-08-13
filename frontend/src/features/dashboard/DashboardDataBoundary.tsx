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
  const [selectedCourseId, setSelectedCourseId] = useState<string | null>(null);
  const courseCount = view.model?.learning.courses.length ?? 0;

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
        if (session === null) { setSelectedCourseId(null); setView({ state: "unauthenticated", model: null }); return; }
        const courses = await fetchCourses({ signal: controller.signal });
        if (!isCurrent(sessionGeneration)) return;
        if (courses.length === 0) { setSelectedCourseId(null); setView({ state: "empty", model: { student: { displayName: session.user.username }, learning: { courses, lessons: [], selectedCourseId: null } } }); return; }
        setSelectedCourseId(courses[0].id);
        setView({ state: "loading", model: { student: { displayName: session.user.username }, learning: { courses, lessons: [], selectedCourseId: courses[0].id } } });
      } catch (error) {
        if (!isCurrent(generation) || (error instanceof DOMException && error.name === "AbortError")) return;
        setSelectedCourseId(null);
        setView({ state: classify(error), model: null });
      }
    })();
    return () => { mounted = false; controller.abort(); generation += 1; };
  }, []);

  useEffect(() => {
    if (selectedCourseId === null || courseCount === 0) return;
    const controller = new AbortController();
    let current = true;
    const courseId = selectedCourseId;
    void fetchLessons(courseId, { signal: controller.signal }).then((lessons) => {
      if (!current) return;
      setView((previous) => previous.model === null ? previous : { state: lessons.length === 0 ? "lessons-empty" : "ready", model: { ...previous.model, learning: { ...previous.model.learning, lessons, selectedCourseId: courseId } } });
    }).catch((error: unknown) => {
      if (!current || (error instanceof DOMException && error.name === "AbortError")) return;
      const state = classify(error);
      if (state === "parent-not-found" || state === "unauthenticated" || state === "forbidden") setSelectedCourseId(null);
      setView({ state, model: null });
    });
    return () => { current = false; controller.abort(); };
  }, [selectedCourseId, courseCount]);

  const selectCourse = (courseId: string) => {
    if (view.model === null || !view.model.learning.courses.some((course) => course.id === courseId)) return;
    setSelectedCourseId(courseId);
    setView({ state: "loading", model: { ...view.model, learning: { ...view.model.learning, lessons: [], selectedCourseId: courseId } } });
  };
  return view.model === null || (view.state !== "ready" && view.state !== "lessons-empty")
    ? <DashboardScreen state={view.state} />
    : <DashboardScreen model={view.model} state={view.state} onSelectCourse={selectCourse} />;
}
