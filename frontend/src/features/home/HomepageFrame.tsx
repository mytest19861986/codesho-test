import type { PublicShellProps } from "@/components/layout";
import { PublicShell } from "@/components/layout";

import { homepageAlphaContent } from "@/content/fa/homepage.alpha";

import { HomeHero } from "./components";
import styles from "./homepageFrame.module.css";

export type HomepageFrameProps = Omit<PublicShellProps, "children">;

export function HomepageFrame(props: HomepageFrameProps) {
  return (
    <PublicShell {...props}>
      <div className={styles.frame}>
        <HomeHero content={homepageAlphaContent.hero} />
      </div>
    </PublicShell>
  );
}
