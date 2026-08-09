export type DashboardViewState = "ready" | "loading" | "empty" | "error";

export interface DashboardStudent {
  readonly displayName: string;
  readonly greeting: string;
  readonly className: string;
}

export interface DashboardLearning {
  readonly course: string;
  readonly module: string;
  readonly lesson: string;
  readonly progress: number;
  readonly totalUnits: number;
  readonly completedUnits: number;
}

export interface DashboardSession {
  readonly title: string;
  readonly date: string;
  readonly time: string;
  readonly type: string;
  readonly status: string;
}

export interface DashboardMomentum {
  readonly xp: number;
  readonly rank: string;
  readonly streak: number;
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
