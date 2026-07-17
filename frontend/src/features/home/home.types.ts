export type HomepageRoute = "/login" | "/signup" | "/paths" | "/courses" | "/projects" | "/mentor";

export type HomepageDestinationStatus = "available" | "hidden_until_route_available";

export type HomepageSectionStatus =
  | "enabled"
  | "hidden_until_verified_data"
  | "omitted_until_permissioned"
  | "hidden_until_route_available";

export type HomepageAssetStatus = "generation_authorized" | "awaiting_official_asset";

export type HomepageAssetApprovalStatus = "alpha_approved";

export type HomepageAssetBackground = "solid";

export type HomepageAssetPresentation = "decorative";

export type HomepageProductionRights = "pending_metadata_review";

export type HomepageAssetSourceKind = "employer_supplied_ai_generated";

export type HomepageReferenceUse = "none_reported_not_independently_verified";

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

export interface HomepageAssetMetadata {
  readonly id: "home-hero-ai-coding-alpha";
  readonly src: "/assets/home/hero-ai-coding-alpha.png";
  readonly width: 1448;
  readonly height: 1086;
  readonly format: "png";
  readonly background: HomepageAssetBackground;
  /** Coupled invariant: decorative presentation requires an empty alt value. */
  readonly presentation: HomepageAssetPresentation;
  readonly alt: "";
  readonly approvalStatus: HomepageAssetApprovalStatus;
  /** Provisional only; never treat this value as cleared for Production use. */
  readonly productionRights: HomepageProductionRights;
  readonly sourceKind: HomepageAssetSourceKind;
  /** Unknown at Alpha; do not infer or backfill attribution. */
  readonly provider: null;
  /** Unknown at Alpha; do not infer or backfill attribution. */
  readonly model: null;
  readonly referenceUse: HomepageReferenceUse;
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
    readonly illustration: HomepageAssetMetadata;
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
