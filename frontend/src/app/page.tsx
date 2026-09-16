import type { Metadata } from "next";

import { homepageAlphaContent } from "@/content/fa/homepage.alpha";
import { HomepageFrame } from "@/features/home/HomepageFrame";

const homepageTitle = `${homepageAlphaContent.brandName} | ${homepageAlphaContent.hero.title}`;

const availableNavigationItems = homepageAlphaContent.navigation
  .filter((item) => item.destination.status === "available" && item.id !== "login")
  .map((item) => ({
    id: item.id,
    label: item.label,
    href: item.destination.route,
  }));

const loginNavItem = homepageAlphaContent.navigation.find((item) => item.id === "login");

const homepageShell = {
  brand: homepageAlphaContent.brandName,
  drawerCloseLabel: homepageAlphaContent.shell.drawerCloseLabel,
  footerGroups: [
    {
      id: "paths",
      label: homepageAlphaContent.learningPathsHeading,
      links: homepageAlphaContent.learningPaths.map((p) => ({
        id: p.id,
        label: p.title,
        href: p.action.destination.route,
      })),
    },
    {
      id: "auth",
      label: homepageAlphaContent.brandName,
      links: [
        {
          id: "footer-login",
          label: loginNavItem ? loginNavItem.label : homepageAlphaContent.brandName,
          href: loginNavItem ? loginNavItem.destination.route : "/login",
        },
      ],
    },
  ],
  menuButtonLabel: homepageAlphaContent.shell.menuButtonLabel,
  navigationItems: availableNavigationItems,
  navigationLabel: homepageAlphaContent.shell.navigationLabel,
  actionSlot: loginNavItem ? (
    <a className="button primary" href={loginNavItem.destination.route}>
      {loginNavItem.label}
    </a>
  ) : undefined,
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
