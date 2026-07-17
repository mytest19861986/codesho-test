import type { Metadata } from "next";

import { homepageAlphaContent } from "@/content/fa/homepage.alpha";
import { HomepageFrame } from "@/features/home/HomepageFrame";

const homepageTitle = `${homepageAlphaContent.brandName} | ${homepageAlphaContent.hero.title}`;

const homepageShell = {
  brand: homepageAlphaContent.brandName,
  drawerCloseLabel: homepageAlphaContent.shell.drawerCloseLabel,
  footerGroups: [],
  menuButtonLabel: homepageAlphaContent.shell.menuButtonLabel,
  navigationItems: [],
  navigationLabel: homepageAlphaContent.shell.navigationLabel,
};

export const metadata: Metadata = {
  title: homepageTitle,
  description: homepageAlphaContent.hero.description,
  openGraph: {
    title: homepageTitle,
    description: homepageAlphaContent.hero.description,
  },
};

export default function Home() {
  return <HomepageFrame {...homepageShell} />;
}
