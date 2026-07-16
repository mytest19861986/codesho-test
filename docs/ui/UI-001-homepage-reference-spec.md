# UI-001 Homepage Reference Specification

- Approved reference: `H:\codesho\UI\UI-001-homepage-reference.png`
- SHA-256: `53647698B51BE216289D670D75D411FEED701CCC87096E6812E7024D5921D9AD`
- Reference asset is intentionally external to the repository and production output.
- Gemini Review 01 prompt: `GEMINI_UI_001_REFERENCE_ANALYSIS_V1`
- Gemini Review 01 result: `GEMINI_UI_001_REFERENCE_ANALYSIS_COMPLETED`
- Gemini Review 02 result: `GEMINI_UI_001_VISUAL_REVIEW_COMPLETED`
- Raw Gemini prompt and response are retained outside the repository under
  `H:\codesho\UI\gemini-review\`.

## Locked order

1. Header, hero, statistics and floating AI mentor card
2. Why Codesho feature cards
3. Learning paths
4. Project cards
5. AI mentor banner
6. Footer

The reference’s two supplied panels are one vertical page; they are not a
side-by-side layout.

## Implementation notes

The repository contained no approved logo, laptop illustration, project-card
images, or self-hosted Persian font. These visual assets are recreated with
semantic HTML, CSS, and inline text glyphs rather than copied from the locked
reference or replaced by a production bitmap placeholder. The page makes no
remote-font request. Any future supplied brand assets or a licensed self-hosted
Persian font should replace only their corresponding CSS reconstructions.

## Known fidelity risks

- The reference’s detailed laptop/code artwork, logo artwork, and project
  screenshots cannot be reproduced pixel-for-pixel without approved source
  assets.
- Text visible at thumbnail-scale in the locked reference was transcribed using
  Gemini analysis; uncertain text is not presented as a verified product claim.
- Desktop is the primary target. Tablet and mobile preserve the reference’s
  hierarchy as responsive reflow rather than introducing new sections.

## Temporary checkpoint status

`UI-001_ASSET_BLOCKED` — Commander has not granted final visual approval.
Gemini Review 02 identifies a blocking fidelity gap: the approved source logo,
laptop/mobile mockups, and project preview assets are not available in the
workspace. No remote font, unlicensed font, unknown asset, low-quality image
extraction, or production copy of the locked reference was introduced. The
non-asset corrections from the review (student count, ambient/path glows, and
CSS-only benefit illustrations) are included. Resume final visual review only
after the employer selects either supplied approved assets/font or documented
acceptance of the CSS reconstruction gap.

## UI-001B employer-approved asset-gap disposition

- Employer decision: `OPTION_B_APPROVED`.
- Status: `ACCEPTED_KNOWN_GAP_BY_EMPLOYER_OPTION_B`.
- The CSS-rendered logo, device mockups, and project previews remain temporary
  reconstructions, not source brand or product assets; this does not claim
  pixel-level fidelity for the unavailable imagery.
- Vazirmatn is self-hosted through `next/font/local`; no runtime font CDN or
  remote font request is used.
- Source: official `rastikerdar/vazirmatn` release `v33.003` (tag commit
  `f68f7bc5dd1d046bd6a5a2bda355bd6d430e807a`).
- Imported variable font: `frontend/src/app/fonts/Vazirmatn[wght].woff2`;
  SHA-256: `17E355067C8284F47743A1EE3B1EF7FF684FF0601EDA357F9353B10B3016AB31`.
- License: SIL Open Font License 1.1, preserved at
  `frontend/THIRD_PARTY_LICENSES_Vazirmatn.txt`.
- Technical completion status: `WAITING_EMPLOYER_VISUAL_APPROVAL`.
