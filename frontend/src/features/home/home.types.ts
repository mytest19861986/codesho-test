export type HomepageRoute = "/login" | "/signup" | "/paths" | "/courses" | "/projects" | "/mentor";

export type HomepageDestinationStatus = "available" | "hidden_until_route_available";

export interface HomepageDestination {
  readonly route: HomepageRoute;
  readonly status: HomepageDestinationStatus;
}

export interface HomepageAction {
  readonly id: string;
  readonly label: string;
  readonly destination: HomepageDestination;
}

export type HomepageNavigationItem = HomepageAction;

export interface HomepageFeature {
  readonly id: string;
  readonly title: string;
  readonly description: string;
}

export interface HomepageLearningPath {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly action: HomepageAction;
}

export interface HomepageAlphaContent {
  readonly brandName: string;
  readonly navigation: readonly HomepageNavigationItem[];
  readonly hero: {
    readonly eyebrow: string;
    readonly title: string;
    readonly description: string;
    readonly primaryAction: HomepageAction;
    readonly secondaryAction: HomepageAction;
  };
  readonly features: readonly HomepageFeature[];
  readonly learningPaths: readonly HomepageLearningPath[];
  readonly mentor: {
    readonly eyebrow: string;
    readonly title: string;
    readonly description: string;
    readonly action: HomepageAction;
  };
}
