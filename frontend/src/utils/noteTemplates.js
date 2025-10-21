export const NOTE_TEMPLATES = [
  {
    id: 'blank',
    name: 'Blank Note',
    icon: '📝',
    title: '',
    content: '<p></p>',
    tags: [],
  },
  {
    id: 'meeting',
    name: 'Meeting Notes',
    icon: '🤝',
    title: 'Meeting Notes - [Date]',
    content: `<h2>Attendees</h2>
<p></p>
<h2>Agenda</h2>
<ul>
  <li></li>
</ul>
<h2>Discussion Points</h2>
<p></p>
<h2>Action Items</h2>
<ul>
  <li></li>
</ul>
<h2>Next Steps</h2>
<p></p>`,
    tags: ['meeting'],
  },
  {
    id: 'daily',
    name: 'Daily Journal',
    icon: '📅',
    title: 'Daily Journal - [Date]',
    content: `<h2>Today's Goals</h2>
<ul>
  <li></li>
</ul>
<h2>Accomplishments</h2>
<p></p>
<h2>Challenges</h2>
<p></p>
<h2>Learnings</h2>
<p></p>
<h2>Gratitude</h2>
<p></p>`,
    tags: ['journal', 'daily'],
  },
  {
    id: 'research',
    name: 'Research Notes',
    icon: '🔬',
    title: 'Research: [Topic]',
    content: `<h2>Research Question</h2>
<p></p>
<h2>Key Findings</h2>
<ul>
  <li></li>
</ul>
<h2>Sources</h2>
<p></p>
<h2>Methodology</h2>
<p></p>
<h2>Conclusions</h2>
<p></p>
<h2>Further Reading</h2>
<p></p>`,
    tags: ['research'],
  },
  {
    id: 'idea',
    name: 'Idea Capture',
    icon: '💡',
    title: 'Idea: [Brief Description]',
    content: `<h2>The Idea</h2>
<p></p>
<h2>Problem It Solves</h2>
<p></p>
<h2>Potential Applications</h2>
<ul>
  <li></li>
</ul>
<h2>Next Steps</h2>
<p></p>
<h2>Related Ideas</h2>
<p></p>`,
    tags: ['idea'],
  },
  {
    id: 'project',
    name: 'Project Planning',
    icon: '📋',
    title: 'Project: [Name]',
    content: `<h2>Project Overview</h2>
<p></p>
<h2>Goals & Objectives</h2>
<ul>
  <li></li>
</ul>
<h2>Timeline</h2>
<p></p>
<h2>Resources Needed</h2>
<ul>
  <li></li>
</ul>
<h2>Milestones</h2>
<p></p>
<h2>Risks & Mitigation</h2>
<p></p>`,
    tags: ['project', 'planning'],
  },
]
