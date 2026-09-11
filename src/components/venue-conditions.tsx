const notes: Record<string, { text: string; source: string; label: string }> = {
  "Melbourne Cricket Ground": {
    text: "The MCG describes roof cover over some seating sections and does not guarantee protection from the weather. Seating cover alone does not establish conditions on the field.",
    source:
      "https://www.mcg.org.au/plan-a-visit/seating-and-ticket-information/seating-maps",
    label: "MCG seating and weather guidance",
  },
  "SoFi Stadium": {
    text: "SoFi’s official guide describes a fixed roof. That building detail does not establish the wind, temperature or other conditions on the field at kickoff.",
    source: "https://www.sofistadium.com/plan-your-visit/a-z-guide",
    label: "SoFi Stadium official guide",
  },
};

export function VenueConditions({ venue }: { venue: string }) {
  const note = notes[venue];
  if (!note) return null;
  return (
    <p className="fine">
      {note.text}{" "}
      <a href={note.source} target="_blank" rel="noreferrer">
        {note.label} ↗
      </a>
    </p>
  );
}
