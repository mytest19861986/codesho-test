export type DashboardViewState = "ready" | "loading" | "empty" | "error";

export interface DashboardStudent {
  readonly displayName: string;
  readonly greeting: string;
  readonly contextLabel: string;
}

export interface DashboardLearning {
  readonly course: string;
  readonly module: string;
  readonly lesson: string;
  readonly progress: number | null;
  readonly totalUnits: number | null;
  readonly completedUnits: number | null;
}

export interface DashboardSession {
  readonly title: string;
  readonly date: string;
  readonly time: string;
  readonly type: string;
  readonly status: string;
}

export interface DashboardMomentum {
  readonly xp: number | null;
  readonly rank: string;
  readonly streak: number | null;
}

export interface DashboardAssignment {
  readonly title: string;
  readonly dueLabel: string;
  readonly status: string;
  readonly actionLabel: string;
}

export interface DashboardRecommendation {
  readonly title: string;
  readonly reason: string;
}

export interface DashboardModel {
  readonly student: DashboardStudent;
  readonly learning: DashboardLearning;
  readonly nextSession: DashboardSession;
  readonly momentum: DashboardMomentum;
  readonly assignment: DashboardAssignment;
  readonly recommendation: DashboardRecommendation;
  readonly attention: readonly string[];
}
