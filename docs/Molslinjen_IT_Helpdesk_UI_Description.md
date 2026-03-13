# Molslinjen IT Helpdesk – UI Design Description
*For use with Google Stitch or any UI design tool*

---

## Overall Design Language

A modern, clean enterprise chat interface with a maritime identity. The design uses a cool blue primary palette against neutral grays and white. Rounded corners throughout (8–24px), subtle shadows, and smooth hover transitions give it a polished, professional feel. Typography is Inter/Segoe UI — sharp and legible. The tone is calm, trustworthy, and efficient.

---

## Color Palette

| Role | Hex | Usage |
|---|---|---|
| Primary Blue | `#0052CC` | Buttons, links, active states |
| Blue Dark | `#003d99` | Hover states |
| Blue Light | `#e8f0fe` | Tinted backgrounds, selected states |
| Green | `#00875A` | Success, positive feedback |
| Red | `#DE350B` | Errors, negative feedback |
| Orange | `#FF8B00` | Warnings, escalation alerts |
| Gray-800 | `#202124` | Primary body text |
| Gray-600 | `#5f6368` | Secondary / muted text |
| Gray-200 | `#e8eaed` | Borders, dividers |
| Gray-100 | `#f1f3f4` | Page backgrounds |
| White | `#ffffff` | Cards, surfaces |

---

## Typography

- **Font Family:** Inter, Segoe UI, system-ui, sans-serif
- **Scale:**
  - 11px / weight 600–700 — captions, badges, uppercase labels
  - 13px / weight 500–600 — sidebar items, small buttons
  - 14–14.5px / weight 400 — body text, chat messages
  - 16px / weight 400 — subtitles
  - 24px / weight 700 — section headings
  - 28px / weight 700 — welcome screen title
  - 32px / weight 800 — stat numbers on dashboard
- **Line height:** 1.5 general, 1.6 in chat bubbles

---

## Screen 1: Login Screen

### Layout
Full-viewport screen. A photograph of the Molslinjen ferry at sea fills the background at 45% opacity, overlaid with a dark navy gradient (`#1a3a5c` → `#0a1f35`). The ferry hull with the "MOLSLINJEN" logo is visible on the left side of the image.

### Card
Positioned on the right side of the screen (roughly the right 45%). Frosted glass effect: `rgba(255,255,255,0.50)` background with `blur(4px)` backdrop filter. 24px border-radius, strong drop shadow. Max width 620px. Padding scales responsively with viewport size using CSS clamp.

### Card Contents (top to bottom)

1. **Title:** "Welcome to IT Helpdesk" — 24px bold, dark gray `#202124`
2. **Subtitle:** "Enter your name to continue" — 14px, muted gray `#5f6368`, 32px margin below
3. **Name input field:** Full-width white input. 2px gray border (`#e8eaed`), 12px border-radius, 14px 16px padding. Blue focus ring (`#0052CC`). Placeholder text in gray.
4. **Role selector:** Two side-by-side cards:
   - Left: "Employee" with person icon + description "IT help & support"
   - Right: "IT Admin" with shield icon + description "Dashboard & logs"
   - Each card: gray-50 background, 2px gray border, 12px radius
   - Active/selected: blue border `#0052CC`, light blue background `#e8f0fe`
   - Label: 13px bold dark gray. Description: 11px muted gray.
5. **Start Chat button:** Full-width, `#0052CC` blue fill, white text, 12px radius. Disabled state: muted light blue `#a8c4e8` with lighter text.
6. **Divider:** "or" centered between two horizontal lines (`rgba(0,0,0,0.2)`). Dark gray text, 12px.
7. **Microsoft SSO button:** White background, 2px gray border, 12px radius. Microsoft four-square logo left-aligned inside button. "Continue with Microsoft" text, 14px semibold. Hover: blue border, very light blue background tint.

### Top-right Corner
Language toggle pill — "DA" / "EN" — frosted glass style (`rgba(255,255,255,0.15)` background), white text, semi-transparent border, 20px border-radius pill shape.

### Responsive Behavior
- ≤768px: Card centers, full width, border-radius reduces to 16px
- ≤480px: Padding tightens, role buttons stack vertically

---

## Screen 2: Main Chat Interface

### Layout
Two-column full-height layout: fixed 268px sidebar on the left + flexible main content area on the right.

---

### Sidebar (Left, 268px)

**Background:** White. 1px gray-200 right border.

**Logo row:**
- 32px Molslinjen wave icon
- "IT Helpdesk" in blue (`#0052CC`) bold 15px
- "Molslinjen IT Support" in gray 11px
- Bottom border divider

**New Chat button:**
- Full-width, solid blue `#0052CC`, white text
- "+ New chat" label, 13px weight 600
- 8px border-radius, 10px 14px padding
- Hover: darker blue `#003d99`

**Ticket Lookup section:**
- Label: "CHECK TICKET STATUS" — 11px uppercase, gray, letter-spacing
- Row: text input (border, 8px radius) + blue search icon button
- Result card when found: light gray background, blue monospace ticket ID, color-coded status badge, summary text, creation date

**Status Badge Colors:**
- Open: blue tint (`#e3f2fd` bg / `#1565c0` text)
- In Progress: orange tint (`#fff3e0` bg / `#e65100` text)
- Pending: red tint (`#fce4ec` bg / `#c62828` text)
- Resolved: green tint (`#e8f5e9` bg / `#2e7d32` text)

**Bottom section:**
- Language switch button (globe icon + label)
- IT Support contact block: phone, email, hours with icons
- 13px gray text, subtle dividers between blocks

---

### Main Chat Area (Right)

**Background:** Light gray `#f8f9fa`

#### Welcome State (no messages yet)
Vertically centered content:
- Large greeting: "Hi [Name]! 👋" — 28px bold, dark gray
- Subtitle: "What can I help you with today?" — 16px gray, 28px below title
- Suggestion chips: wrapping flex grid of pill-shaped buttons (20px border-radius, white, gray border). Hover: blue border + light blue fill + slight lift animation. Max width 680px, centered.

#### Message Thread
- 20px vertical gap between messages
- **User messages:** Right-aligned. Green circle avatar (34px) with user initials. Blue bubble (`#0052CC`), white text, sharp bottom-right corner (4px radius), other corners 16px.
- **Bot messages:** Left-aligned. Blue circle avatar "IT" (34px). White bubble, gray border, sharp bottom-left corner. Below: "Sources: ..." in 11.5px gray with document icon. Below that: thumbs up/down feedback buttons (gray by default, green/red when selected).

#### Escalation Card
Amber card (`#fff8e1`) with orange "Need more help?" header. Two action buttons:
- "Create Ticket" — blue filled, white text
- "Contact IT" — white background, gray border

#### Typing Indicator
Three gray dots bouncing in a white bubble (bot-style). Staggered 0.2s animation delay between each dot.

---

### Input Bar (Bottom)
- Light gray background, 1px top border
- Rounded input container: white fill, 2px gray border, 14px border-radius, blue border on focus
- Placeholder: "Ask a question..."
- Right side: 40×40px blue send button with arrow icon, 10px border-radius
- Hover: slightly darker blue + subtle scale-up

---

## Screen 3: Admin Dashboard

### Header Bar
- White, 60px height, 1px gray bottom border
- Left: Logo + "IT Helpdesk" title
- Center: Tab navigation — "Overview", "Tickets", "Conversations"
  - Active tab: `#0052CC` text, 3px blue bottom border
  - Inactive: gray-600 text, no border
- Right: "Back to Chat" outlined button

### Stats Row
4 equal-width white cards in a horizontal grid. Each card:
- 12px border-radius, subtle shadow
- Large number (32px, weight 800) in brand color
- Small label beneath (12px gray-600)
- Colors: blue, green, orange, purple for each stat

### Content Panels (2-column grid below stats)

**Top Questions panel:**
- White, 12px radius, shadow
- Ranked list: rank number (gray) + question text + count badge (blue pill)

**Satisfaction Stats panel:**
- Large thumbs up / thumbs down numbers, labels, vertical divider

**Recent Tickets table:**
- Column headers: 11px uppercase, gray, letter-spacing
- Rows: ticket ID (blue monospace), summary, status badge, date
- Row hover: light gray background

**Escalated Conversations list:**
- Expandable rows — click to reveal conversation log
- Shows message count + timestamp
- Expanded view: scrollable conversation log with padding

---

## Modals

### Ticket Detail Modal

**Overlay:** Semi-transparent black (`rgba(0,0,0,0.45)`), fade-in animation

**Modal box:**
- White background, 16px border-radius
- Max width 520px
- Drop shadow: `0 20px 60px rgba(0,0,0,0.25)`
- Slide-up entry animation

**Modal Header:**
- 40×40px blue icon square (10px radius)
- Ticket ID in blue monospace 17px bold
- Close (×) button top-right

**Status banner:**
- Full-width colored strip (matches badge colors)
- Status label + icon, 13px semibold

**Details section:**
- Label/value pairs: label in 11px uppercase gray, value in 14px dark gray
- Flex column, 14px gap

**Description block:**
- Gray-50 background, gray border, 8px radius
- Scrollable if long (max-height 180px)

**Footer:**
- Close button — blue filled, 14px, 8px radius

---

## Key Interaction Details

- All hover states: `0.2s` transition
- Hoverable cards lift with `translateY(-1px)` micro-animation
- Chat bubbles have one sharp "tail" corner (4px) and three rounded corners (16px)
- Inputs get blue focus rings, no outline
- Buttons scale slightly on hover (`scale(1.05)`)
- Modal appears with `slideUp` animation (0.2s ease)

---

## Responsive Breakpoints

| Breakpoint | Behavior |
|---|---|
| ≤480px | Login padding tightens, role buttons stack vertically |
| ≤768px | Login card centers, full width |
| ≤700px | Chat sidebar hidden, message padding reduced |
| ≤900px | Admin stats grid → 2 columns, panels → 1 column |
