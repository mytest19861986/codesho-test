import type { HomepageSectionStatus } from "../home.types";

import styles from "./trustStrip.module.css";

export interface TrustStripProps {
  readonly status: HomepageSectionStatus;
}

export function TrustStrip({ status }: TrustStripProps) {
  if (status !== "enabled") return null;

  return <section className={styles.strip} />;
}
