"use client";

import { useAppDispatch, useAppSelector } from "../lib/hooks";
import { setView } from "../lib/searchSlice";

export default function ViewToggle() {
  const view = useAppSelector((state) => state.search.view);
  const selectedScene = useAppSelector((state) => state.search.selectedScene);
  const dispatch = useAppDispatch();

  // NDVI is computed for one scene, so it needs one. Without a scene the map shows the default image.
  const showingNdvi = view === "ndvi" && selectedScene !== null;

  return (
    <section>
      <h2>View</h2>
      <div style={{ display: "flex", gap: 6 }}>
        <button
          aria-pressed={!showingNdvi}
          onClick={() => dispatch(setView("true-colour"))}
          style={{ fontWeight: showingNdvi ? 400 : 700 }}
        >
          True colour
        </button>
        <button
          aria-pressed={showingNdvi}
          disabled={selectedScene === null}
          onClick={() => dispatch(setView("ndvi"))}
          style={{ fontWeight: showingNdvi ? 700 : 400 }}
        >
          NDVI
        </button>
      </div>
      {selectedScene === null && <p style={{ margin: "4px 0", fontSize: 13 }}>Pick a scene to see its NDVI.</p>}
    </section>
  );
}
