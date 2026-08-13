import type { DashboardModel } from "./dashboard.types";

/** Typed empty fixture retained for focused component-contract tests. */
export const dashboardFixture: DashboardModel = {
  student: { displayName: "آرین" },
  learning: { courses: [], lessons: [], selectedCourseId: null },
};
