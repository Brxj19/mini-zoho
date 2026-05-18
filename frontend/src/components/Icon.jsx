const iconPaths = {
  dashboard: ["M4 13h7V4H4zm9 0h7V4h-7zM4 20h7v-5H4zm9 0h7v-9h-7z"],
  box: ["M12 3 4.5 7.2v9.6L12 21l7.5-4.2V7.2L12 3Z", "M4.5 7.2 12 11l7.5-3.8", "M12 11v10"],
  layers: ["m12 3 8 4-8 4-8-4 8-4Z", "m4 11 8 4 8-4", "m4 15 8 4 8-4"],
  sliders: ["M4 6h7", "M15 6h5", "M10 6v12", "M4 18h7", "M15 18h5", "M14 6v12"],
  shuffle: ["m16 3 5 5-5 5", "M21 8h-5a5 5 0 0 0-4.2 2.3L9 14.5A5 5 0 0 1 4.8 17H3", "m8 21-5-5 5-5", "M3 8h1.8A5 5 0 0 1 9 10.3l2.8 4.2A5 5 0 0 0 16 17h5"],
  warehouse: ["M3 10.5 12 4l9 6.5V20H3z", "M9 20v-6h6v6"],
  alert: ["M12 9v4", "M12 17h.01", "M10.3 3.9 2.6 18A2 2 0 0 0 4.3 21h15.4a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0Z"],
  users: ["M16 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2", "M9.5 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M20 8v6", "M23 11h-6"],
  cart: ["M6 6h15l-1.5 8h-11Z", "M6 6 5 3H2", "M9 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z", "M18 21a1 1 0 1 0 0-2 1 1 0 0 0 0 2Z"],
  package: ["M12 2 3 7l9 5 9-5-9-5Z", "M3 7v10l9 5 9-5V7", "M12 12v10"],
  receipt: ["M7 3h10v18l-3-2-2 2-2-2-3 2Z", "M9 8h6", "M9 12h6", "M9 16h4"],
  undo: ["M9 14 4 9l5-5", "M20 20a8 8 0 0 0-8-8H4"],
  briefcase: ["M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2", "M4 7h16v12H4z", "M4 12h16"],
  clipboard: ["M9 3h6l1 2h3v16H5V5h3l1-2Z", "M9 3v2h6V3"],
  truck: ["M10 17h4", "M1 5h11v11H1z", "M12 8h5l3 3v5h-8", "M5.5 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z", "M17.5 19a1.5 1.5 0 1 0 0-3 1.5 1.5 0 0 0 0 3Z"],
  bill: ["M6 3h12v18l-3-2-3 2-3-2-3 2Z", "M9 8h6", "M9 12h6", "M9 16h4"],
  chart: ["M4 19h16", "M7 16V9", "M12 16V5", "M17 16v-4"],
  activity: ["M3 12h4l3 6 4-12 3 6h4"],
  shield: ["M12 3 5 6v6c0 4.4 2.6 8.5 7 10 4.4-1.5 7-5.6 7-10V6l-7-3Z"],
  userCog: ["M12 14a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M5 21a7 7 0 0 1 14 0", "M19 8l1 .6 1-.6v1.2l1 .6-1 .6v1.2l-1-.6-1 .6v-1.2l-1-.6 1-.6z"],
  building: ["M4 21V5l8-2v18", "M12 9h8v12h-8", "M7 8h.01", "M7 12h.01", "M7 16h.01", "M16 12h.01", "M16 16h.01"],
  sparkles: ["M12 3l1.5 4.5L18 9l-4.5 1.5L12 15l-1.5-4.5L6 9l4.5-1.5Z", "m19 16 .8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8Z", "m5 14 .7 1.8L7.5 16l-1.8.7L5 18.5l-.7-1.8L2.5 16l1.8-.7Z"],
  settings: ["M12 8a4 4 0 1 0 0 8 4 4 0 0 0 0-8Z", "M3 12h2", "M19 12h2", "M12 3v2", "M12 19v2", "m5.6 5.6 1.4 1.4", "m17 17-1.4-1.4", "m18.4 5.6-1.4 1.4", "m7 17-1.4 1.4"],
  stars: ["M12 2l2.3 6.7H21l-5.4 3.9 2.1 6.4L12 15l-5.7 4 2.1-6.4L3 8.7h6.7Z"],
  bell: ["M6 8a6 6 0 1 1 12 0c0 7 3 8 3 8H3s3-1 3-8", "M10 20a2 2 0 0 0 4 0"],
  search: ["m21 21-4.3-4.3", "M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15Z"],
  plus: ["M12 5v14", "M5 12h14"],
  clock: ["M12 7v5l3 3", "M12 22a10 10 0 1 0 0-20 10 10 0 0 0 0 20Z"],
  help: ["M9.1 9a3 3 0 1 1 5.8 1c-.6.9-1.6 1.3-2.1 2.1-.3.4-.4.8-.4 1.4", "M12 17h.01"],
  menu: ["M4 7h16", "M4 12h16", "M4 17h16"],
  chevronRight: ["M9 6l6 6-6 6"],
  chevronDown: ["m6 9 6 6 6-6"],
  more: ["M5 12h.01", "M12 12h.01", "M19 12h.01"],
  export: ["M12 3v12", "m7 8 5-5 5 5", "M5 21h14"],
  import: ["M12 21V9", "m17 16-5 5-5-5", "M5 3h14"],
  filter: ["M4 5h16", "M7 12h10", "M10 19h4"],
  sort: ["M8 7h8", "M8 12h5", "M8 17h2"],
  hash: ["M5 9h14", "M5 15h14", "M10 4 8 20", "M16 4l-2 16"],
  plug: ["M9 7V3", "M15 7V3", "M6 11h12v2a6 6 0 1 1-12 0Z"],
  avatar: ["M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8Z", "M5 21a7 7 0 0 1 14 0"],
};

export function Icon({ name, size = 18, className = "" }) {
  const paths = iconPaths[name] ?? iconPaths.dashboard;

  return (
    <svg
      className={`icon ${className}`.trim()}
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {paths.map((path) => (
        <path key={path} d={path} />
      ))}
    </svg>
  );
}
