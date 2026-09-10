import { ImageResponse } from "next/og";
export const alt = "NFL Intelligence — Know the game. Respect the uncertainty.";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";
export default function Image() {
  return new ImageResponse(
    <div
      style={{
        width: "100%",
        height: "100%",
        display: "flex",
        flexDirection: "column",
        background: "#151a21",
        color: "#edf0f4",
        padding: "68px 80px",
        justifyContent: "space-between",
      }}
    >
      <div style={{ display: "flex", fontSize: 27, color: "#becddd" }}>
        N / NFL Intelligence
      </div>
      <div
        style={{
          display: "flex",
          flexDirection: "column",
          fontSize: 78,
          fontWeight: 700,
          lineHeight: 1.06,
          letterSpacing: -4,
        }}
      >
        <span>Know the game.</span>
        <span style={{ color: "#9da9b9" }}>Respect the uncertainty.</span>
      </div>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          paddingTop: 27,
          borderTop: "1px solid #3d4857",
          fontSize: 21,
          color: "#bac7d8",
        }}
      >
        <span>Independent projections · Transparent evidence</span>
        <span>Every result counts.</span>
      </div>
    </div>,
    size,
  );
}
