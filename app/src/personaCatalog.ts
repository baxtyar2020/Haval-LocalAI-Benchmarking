export type BusinessId = "Consumer" | "Gaming" | "Commercial";

export type PersonaChoice = {
  business: BusinessId;
  name: string;
  blurb: string;
};

export const PERSONA_CHOICES: PersonaChoice[] = [
  { business: "Consumer", name: "Everyday Organizer", blurb: "Lists, schedules, and household plans." },
  { business: "Consumer", name: "Student & Learner", blurb: "Explanations, study guides, and quizzes." },
  { business: "Consumer", name: "Family Coordinator", blurb: "Meals, calendars, and family logistics." },
  { business: "Consumer", name: "Researcher & Shopper", blurb: "Comparisons and buying recommendations." },
  { business: "Consumer", name: "Writer & Communicator", blurb: "Emails, tone, and documents." },
  { business: "Consumer", name: "Creative Prosumer", blurb: "Scripts, captions, and content packages." },
  { business: "Consumer", name: "Personal Adviser", blurb: "Options, risks, and personal plans." },
  { business: "Consumer", name: "Technical Hobbyist", blurb: "PC fixes, commands, and repair plans." },
  { business: "Gaming", name: "Casual Gamer", blurb: "Quick tips, settings, and game picks." },
  { business: "Gaming", name: "Power Player", blurb: "Graphics settings and performance plans." },
  { business: "Gaming", name: "Progressive Creator", blurb: "Titles, scripts, and video packages." },
  { business: "Gaming", name: "Rising Game Developer", blurb: "Code snippets, debug, and small features." },
  { business: "Commercial", name: "Executive & Decision Maker", blurb: "Briefs, risks, and decisions." },
  { business: "Commercial", name: "Project & Operations Manager", blurb: "Owners, status, and program plans." },
  { business: "Commercial", name: "Engineer & Software Developer", blurb: "Errors, functions, tests, and implementation." },
  { business: "Commercial", name: "Analyst & Finance Professional", blurb: "Numbers, trends, and financial reports." },
  { business: "Commercial", name: "Research & Product Professional", blurb: "Comments, competitors, and findings." },
  { business: "Commercial", name: "Sales & Marketing Professional", blurb: "Outreach, claims, and proposals." },
  { business: "Commercial", name: "Customer Support Specialist", blurb: "Tickets, diagnosis, and replies." },
  { business: "Commercial", name: "People, Legal & Compliance Professional", blurb: "Clauses, policies, and obligations." },
];

export const BUSINESSES: { id: BusinessId; label: string; icon: string; note: string }[] = [
  { id: "Consumer", label: "Home & everyday", icon: "house", note: "Lists, learning, shopping, writing." },
  { id: "Gaming", label: "Play & make games", icon: "gamepad-2", note: "Tips, settings, clips, and code." },
  { id: "Commercial", label: "Work & decisions", icon: "briefcase", note: "Briefs, tickets, numbers, and policy." },
];

export const PERSONA_ICONS: Record<string, string> = {
  "Everyday Organizer": "list-checks",
  "Student & Learner": "graduation-cap",
  "Family Coordinator": "users",
  "Researcher & Shopper": "shopping-bag",
  "Writer & Communicator": "pen-line",
  "Creative Prosumer": "camera",
  "Personal Adviser": "heart",
  "Technical Hobbyist": "wrench",
  "Casual Gamer": "gamepad-2",
  "Power Player": "trophy",
  "Progressive Creator": "clapperboard",
  "Rising Game Developer": "code-2",
  "Executive & Decision Maker": "landmark",
  "Project & Operations Manager": "kanban",
  "Engineer & Software Developer": "terminal",
  "Analyst & Finance Professional": "calculator",
  "Research & Product Professional": "microscope",
  "Sales & Marketing Professional": "megaphone",
  "Customer Support Specialist": "headphones",
  "People, Legal & Compliance Professional": "scale",
};
