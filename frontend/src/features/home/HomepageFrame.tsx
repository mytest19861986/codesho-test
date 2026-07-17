import type { PublicShellProps } from "@/components/layout";
import { PublicShell } from "@/components/layout";

import { homepageAlphaContent } from "@/content/fa/homepage.alpha";

import { FinalCta, HomeHero, LearningPathGrid, MentorCta, TrustStrip } from "./components";
import styles from "./homepageFrame.module.css";

export type HomepageFrameProps = Omit<PublicShellProps, "children">;

export function HomepageFrame(props: HomepageFrameProps) {
  return (
    <PublicShell {...props}>
      <div className={styles.frame}>
        <HomeHero content={homepageAlphaContent.hero} />
        <LearningPathGrid heading={homepageAlphaContent.learningPathsHeading} paths={homepageAlphaContent.learningPaths} />
        <TrustStrip status={homepageAlphaContent.sections.trust} />
        <MentorCta content={homepageAlphaContent.mentor} />
        <FinalCta content={homepageAlphaContent.finalCta} />
      </div>
    </PublicShell>
  );
}
