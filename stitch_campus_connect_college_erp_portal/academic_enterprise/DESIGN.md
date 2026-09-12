---
name: Academic Enterprise
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#434655'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#747686'
  outline-variant: '#c4c5d7'
  surface-tint: '#2151da'
  primary: '#0037b0'
  on-primary: '#ffffff'
  primary-container: '#1d4ed8'
  on-primary-container: '#cad3ff'
  inverse-primary: '#b7c4ff'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#004f35'
  on-tertiary: '#ffffff'
  tertiary-container: '#006948'
  on-tertiary-container: '#76eab6'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dce1ff'
  primary-fixed-dim: '#b7c4ff'
  on-primary-fixed: '#001551'
  on-primary-fixed-variant: '#0039b5'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#85f8c4'
  tertiary-fixed-dim: '#68dba9'
  on-tertiary-fixed: '#002114'
  on-tertiary-fixed-variant: '#005137'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  display-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-xl:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.015em
  headline-lg:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
    letterSpacing: -0.01em
  headline-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '600'
    lineHeight: 24px
    letterSpacing: -0.005em
  headline-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
  body-lg:
    fontFamily: Inter
    fontSize: 15px
    fontWeight: '400'
    lineHeight: 22px
  body-md:
    fontFamily: Inter
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  body-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
  label-md:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.04em
  label-sm:
    fontFamily: Inter
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
    letterSpacing: 0.05em
  tabular-numeric:
    fontFamily: JetBrains Mono
    fontSize: 13px
    fontWeight: '500'
    lineHeight: 18px
    letterSpacing: -0.02em
  tabular-numeric-sm:
    fontFamily: JetBrains Mono
    fontSize: 11px
    fontWeight: '500'
    lineHeight: 14px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  gutter: 1rem
  gutter-compact: 0.5rem
  margin: 1.5rem
  margin-mobile: 1rem
  space-xs: 0.25rem
  space-sm: 0.5rem
  space-md: 0.75rem
  space-lg: 1rem
  space-xl: 1.5rem
---

## Brand & Style

This design system delivers an authoritative, high-density institutional enterprise interface tailored for higher education governance, administration, and academic operations. The aesthetic merges executive SaaS rigor with academic pedigree: deep slate foundations convey stability and governance, while vibrant institutional cobalt provides active navigational focus and precise interactive clarity.

The target audience comprises college chancellors, department deans, registrars, faculty, and academic counselors who parse dense data sets, manage compliance, coordinate schedules, and track real-time student outcomes. 

The emotional tone balances high-trust operational reliability with modern administrative efficiency. The visual style is **Corporate / Modern High-Density**, relying on structural borders, micro-elevation, tabular typography alignments, and high-visibility status taxonomies rather than ornamental decoration.

## Colors

The palette establishes an unambiguous hierarchy between administrative command surfaces and active operational work areas:

- **Primary (`#1D4ED8`)**: Institutional Cobalt. Used exclusively for core calls-to-action, primary selection states, active tab indicators, and verified data highlights.
- **Secondary (`#0F172A`)**: Midnight Slate. Applied across structural navigation envelopes—persistent sidebars, master system headers, and root navigational switches—creating an anchor of institutional authority.
- **Tertiary (`#059669`)**: Scholastic Emerald. Dedicated to positive operational telemetry: verified attendance thresholds (e.g., >75%), compliant grading statuses, accredited marks, and confirmed tuition payments.
- **Neutral (`#64748B`)**: Structural Slate. Scales from deep charcoal text hierarchy (`#0F172A`, `#334155`) down through utilitarian sub-labels (`#64748B`), structural hairline dividers (`#E2E8F0`), and soft canvas fields (`#F8FAFC`).

### Semantic & Warning Architecture
- **Warning / Pending (`#D97706`)**: Amber Gold. Denotes academic probation watches, pending document verification, incomplete syllabus tracks, and low-attendance warnings.
- **Critical / Danger (`#E11D48`)**: Academic Rose Red. Flags fee defaults, disciplinary actions, attendance drops below statutory requirements, and irreversible records deletion.
- **Surface Foundations**:
  - Global Canvas: `#F8FAFC` (Slate Canvas)
  - Card & Container Fill: `#FFFFFF` (Pure White)
  - Structural Hairlines: `#E2E8F0` (Slate Border 100)
  - Secondary Inset Fills: `#F1F5F9` (Muted Data Wells & Table Headers)

## Typography

The typographical structure is engineered specifically for dense data consumption, enterprise legibility, and high-frequency analytical review.

- **Primary Interface Type (`Inter`)**: Handles structural hierarchies, UI labels, navigational elements, and narrative student notes. Inter's tall x-height and clear letterforms ensure effortless reading within compressed data tables and multi-column forms.
- **Tabular Mono Type (`JetBrains Mono`)**: Serves enterprise tabular metrics, PRN (Permanent Registration Numbers), student IDs, course ledger codes, timestamps, cumulative GPA figures, and financial balance ledgers.
- **Hierarchy Rules**:
  - Display and Section titles use tight letter spacing (`-0.01em` to `-0.02em`) to maintain optical density without sprawling across functional header space.
  - Sub-labels, table column headers, and administrative badges utilize uppercase styling with deliberate tracking (`0.04em` to `0.05em`) in `label-sm` or `label-md`.
  - Body text settles on an enterprise standard `13px` base (`body-md`), preserving vertical canvas efficiency while exceeding accessibility contrast benchmarks.

## Layout & Spacing

The design system operates on an uncompromising 4px-baseline enterprise grid optimized for high-density 1080p and 1440p desktop displays typical of college administrative departments.

### Layout Model
- **Structural Frame**:
  - Persistent Dual Navigation: Fixed 260px primary navigation sidebar (`#0F172A`) paired with a 56px global utility and context header.
  - Content Workspace: Fluid layout spanning 12 columns with standard `1rem` gutters (`0.5rem` for high-density matrix sheets), framed by a outer workspace inset of `1.5rem`.
- **Vertical Spacing Cadence**:
  - Component internals strictly follow tight spacing tokens (`space-xs` = 4px, `space-sm` = 8px, `space-md` = 12px, `space-lg` = 16px).
  - High-density data matrices lock table row heights to 40px (standard) or 32px (condensed audit log).
- **Responsive Adaptations**:
  - Desktop (>1280px): Persistent primary sidebar; full-width 12-column dynamic dashboards; multi-pane modal drawers.
  - Tablet Landscape (1024px - 1279px): Sidebar collapses into an icon-rail (64px); 8-column canvas; secondary meta panels convert to off-canvas sheets.
  - Mobile (<1023px): Nav turns into an off-canvas drawer; gutters collapse to `0.5rem`, outer margin to `1rem`; tables gain horizontal scroll pinning with sticky student identity columns.

## Elevation & Depth

To avoid visual fatigue during sustained operational use, elevation prioritizes crisp mechanical planes, crisp borders, and subtle tinted ambient drop shadows rather than dramatic blur radii.

- **Level 0 (Workspace Base)**: `#F8FAFC`. Zero elevation, non-interactive root canvas.
- **Level 1 (Card & Content Blocks)**: `#FFFFFF` surface framed by a solid `1px solid #E2E8F0` border and an ambient micro-shadow: `0 1px 2px 0 rgba(15, 23, 42, 0.04)`.
- **Level 2 (Interactive Hover & Dropdowns)**: Surfaces slightly elevate upon hover or interaction, accompanied by `1px solid #CBD5E1` and an elevated shadow: `0 4px 6px -1px rgba(15, 23, 42, 0.07), 0 2px 4px -2px rgba(15, 23, 42, 0.05)`.
- **Level 3 (Sticky Headers, Popovers & Context Menus)**: Overlays utilize pure white backings, framed by `#94A3B8` borders with crisp, controlled diffusion: `0 10px 15px -3px rgba(15, 23, 42, 0.08), 0 4px 6px -4px rgba(15, 23, 42, 0.03)`.
- **Level 4 (System Modals & Critical Verification Sheets)**: Floating central modal dialogs backed by a semi-translucent slate scrim (`rgba(15, 23, 42, 0.6)`) with high-depth projection: `0 20px 25px -5px rgba(15, 23, 42, 0.12), 0 8px 10px -6px rgba(15, 23, 42, 0.06)`.

## Shapes

The design system employs a **Soft** shape language (`roundedness: 1`). Enterprise administrative efficiency demands crisp architectural geometry that maximizes usable surface area and prevents visual sloppiness in dense grid layouts.

- **Inputs, Buttons, Cells, and Dropdowns**: Standardized border radius of `0.25rem` (4px).
- **Cards, System Containers, and Table Shells**: Outer shells utilize `rounded-lg` of `0.5rem` (8px).
- **Modals and Flyout Sheets**: Elevated modals utilize `rounded-xl` of `0.75rem` (12px).
- **Status Indicators and Badges**: Status badges use an intentional `0.25rem` radius or full circular pill geometry (`9999px`) solely for numerical counts (e.g., notification counts, student roll badge chips).

## Components

### Buttons
- **Primary Button**: Solid `#1D4ED8` background, `#FFFFFF` text, `0.25rem` border radius. 32px height in standard density, 28px in table actions. Hover states transition to `#1E40AF` with a subtle inset focus ring of `2px solid rgba(29, 78, 216, 0.35)`.
- **Secondary Button**: `#FFFFFF` background, `1px solid #E2E8F0` border, `#334155` text. On hover, background shifts to `#F8FAFC` and border to `#CBD5E1`.
- **Destructive Button**: Crimson ghost/solid variations. Solid: `#E11D48` background with `#FFFFFF` text for permanent academic record removals or expulsions.

### Metric Cards (KPI Displays)
- Packaged within a `0.5rem` rounded container with `1px solid #E2E8F0`.
- Comprises an overline category title (`label-sm`, `#64748B`), a bold primary KPI figure (`headline-xl`, JetBrains Mono), and a footer indicator showing week-over-week trends or statutory thresholds using the semantic green/amber/red indicator taxonomy.

### Data Tables
- **Header Row**: 36px height, background `#F8FAFC`, bottom border `1px solid #E2E8F0`. Text is `label-sm` in `#475569` with interactive sort chevrons.
- **Data Rows**: Alternating subtle zebra striping optional, default `#FFFFFF` with `#F8FAFC` hover fill. Bottom border hairline `1px solid #F1F5F9`. Height fixed at 40px for standard records, 32px for compact marksheets.
- **Pinned Columns**: Freeze student PRN/Name columns to the left with an active subtle right-hand drop-shadow border when horizontal scrolling triggers.

### Status Badges & Chips
- Compact dimensions: 20px height, `0.25rem` radius, padding `2px 6px`.
- Composed with tinted, accessible pastel fills and high-contrast text:
  - **Attendance Compliant / Active**: `#ECFDF5` background, `#047857` text, `1px solid #A7F3D0` border.
  - **Attendance Warning / Provisional**: `#FFFBEB` background, `#B45309` text, `1px solid #FDE68A` border.
  - **Detained / Defaulter / Suspended**: `#FFF1F2` background, `#BE123C` text, `1px solid #FECDD3` border.

### Input Fields
- Form controls use 34px height, `#FFFFFF` background, `1px solid #CBD5E1`, and `0.25rem` radius.
- Focus: Outer glow ring of `0 0 0 3px rgba(29, 78, 216, 0.15)` with a solid `#1D4ED8` border.
- Floating helper text or validation errors leverage `body-sm` at high color fidelity.

### Checkboxes & Radios
- 16x16px boxes, `1.5px solid #94A3B8`, `0.125rem` radius for checkboxes; fully circular for radios. Checked state activates solid `#1D4ED8` with a crisp `#FFFFFF` check icon.