export type HomepageRoute = "/login" | "/signup" | "/paths" | "/courses" | "/projects" | "/mentor";

export type HomepageDestinationStatus = "available" | "hidden_until_route_available";

export type HomepageSectionStatus =
  | "enabled"
  | "hidden_until_verified_data"
  | "omitted_until_permissioned"
  | "hidden_until_route_available";

export type HomepageAssetStatus = "generation_authorized" | "awaiting_official_asset";

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

export interface HomepageLearningPath {
  readonly id: string;
  readonly title: string;
  readonly description: string;
  readonly action: HomepageAction;
}

export interface HomepageSectionStates {
  readonly hero: "enabled";
  readonly trust: "hidden_until_verified_data";
  readonly learningPaths: "enabled";
  readonly projects: "hidden_until_verified_data";
  readonly courses: "hidden_until_verified_data";
  readonly mentor: "enabled";
  readonly testimonials: "omitted_until_permissioned";
  readonly finalCta: "enabled";
  readonly footer: "hidden_until_route_available";
}

export interface HomepageAssetStates {
  readonly nonLogoIllustrations: "generation_authorized";
  readonly officialLogo: "awaiting_official_asset";
}

export interface HomepageAlphaContent {
  readonly brandName: "CodeSho";
  readonly navigation: readonly HomepageNavigationItem[];
  readonly sections: HomepageSectionStates;
  readonly assets: HomepageAssetStates;
  readonly hero: {
    readonly eyebrow: string;
    readonly title: string;
    readonly description: string;
    readonly primaryAction: HomepageAction;
    readonly secondaryAction: HomepageAction;
  };
  readonly learningPaths: readonly HomepageLearningPath[];
  readonly mentor: {
    readonly title: string;
    readonly descriptionStatus: "pending_transcription";
    readonly action: HomepageAction;
  };
  readonly finalCta: {
    readonly title: string;
    readonly primaryAction: HomepageAction;
    readonly secondaryAction: HomepageAction;
  };
}
