/** Fallback catalogue if GET /catalogue is unavailable (e.g. static-only preview). */
const FALLBACK_CATALOGUE = [
  { id: "track_001", title: "Desk Lamp Glow", artist: "Nova Circuit", genre: "lo-fi" },
  { id: "track_002", title: "Quiet Keys", artist: "Nova Circuit", genre: "lo-fi" },
  { id: "track_003", title: "Late Assignment", artist: "Nova Circuit", genre: "lo-fi" },
  { id: "track_004", title: "Soft Static", artist: "Nova Circuit", genre: "ambient" },
  { id: "track_005", title: "Cloud Corridor", artist: "Velvet Horizon", genre: "ambient" },
  { id: "track_006", title: "Slow Rain Window", artist: "Velvet Horizon", genre: "ambient" },
  { id: "track_007", title: "Morning Drift", artist: "Velvet Horizon", genre: "ambient" },
  { id: "track_008", title: "Pulse Avenue", artist: "Neon Relay", genre: "electronic" },
  { id: "track_009", title: "Grid Runner", artist: "Neon Relay", genre: "electronic" },
  { id: "track_010", title: "Signal Bloom", artist: "Neon Relay", genre: "electronic" },
  { id: "track_011", title: "Binary Tide", artist: "Neon Relay", genre: "electronic" },
  { id: "track_012", title: "Floor Lights", artist: "Club Aster", genre: "dance" },
  { id: "track_013", title: "Afterglow Beat", artist: "Club Aster", genre: "dance" },
  { id: "track_014", title: "Midnight Crowd", artist: "Club Aster", genre: "dance" },
  { id: "track_015", title: "Sidewalk Sketch", artist: "Paper Kites", genre: "indie" },
  { id: "track_016", title: "Borrowed Jacket", artist: "Paper Kites", genre: "indie" },
  { id: "track_017", title: "Corner Cafe", artist: "Paper Kites", genre: "indie" },
  { id: "track_018", title: "Open Notebook", artist: "Paper Kites", genre: "indie" },
  { id: "track_019", title: "Willow Lane", artist: "Cedar & Clay", genre: "folk" },
  { id: "track_020", title: "Campfire Letters", artist: "Cedar & Clay", genre: "folk" },
  { id: "track_021", title: "Harvest Road", artist: "Cedar & Clay", genre: "folk" },
  { id: "track_022", title: "Stone Bridge", artist: "Cedar & Clay", genre: "folk" },
  { id: "track_023", title: "Amplifier Dust", artist: "Redline Assembly", genre: "rock" },
  { id: "track_024", title: "Highway Static", artist: "Redline Assembly", genre: "rock" },
  { id: "track_025", title: "Broken Chorus", artist: "Redline Assembly", genre: "rock" },
  { id: "track_026", title: "Garage Echo", artist: "Redline Assembly", genre: "rock" },
  { id: "track_027", title: "Blue Hour Trio", artist: "Elm Street Quartet", genre: "jazz" },
  { id: "track_028", title: "Night Bus Solo", artist: "Elm Street Quartet", genre: "jazz" },
  { id: "track_029", title: "Coffee Swing", artist: "Elm Street Quartet", genre: "jazz" },
  { id: "track_030", title: "Soft Brass Rain", artist: "Elm Street Quartet", genre: "jazz" },
  { id: "track_031", title: "Focus Loop", artist: "Nova Circuit", genre: "lo-fi" },
  { id: "track_032", title: "Party Wire", artist: "Club Aster", genre: "dance" },
  { id: "track_033", title: "Feather", artist: "Nujabes", genre: "lo-fi" },
  { id: "track_034", title: "Aruarian Dance", artist: "Nujabes", genre: "lo-fi" },
  { id: "track_035", title: "affection", artist: "Jinsang", genre: "lo-fi" },
  { id: "track_036", title: "An Ending (Ascent)", artist: "Brian Eno", genre: "ambient" },
  { id: "track_037", title: "Music for Airports 1/1", artist: "Brian Eno", genre: "ambient" },
  { id: "track_038", title: "Xtal", artist: "Aphex Twin", genre: "ambient" },
  { id: "track_039", title: "Digital Love", artist: "Daft Punk", genre: "electronic" },
  { id: "track_040", title: "One More Time", artist: "Daft Punk", genre: "electronic" },
  { id: "track_041", title: "Strobe", artist: "deadmau5", genre: "electronic" },
  { id: "track_042", title: "Latch", artist: "Disclosure", genre: "dance" },
  { id: "track_043", title: "Marea (we've lost dancing)", artist: "Fred again..", genre: "dance" },
  { id: "track_044", title: "Feel So Close", artist: "Calvin Harris", genre: "dance" },
  { id: "track_045", title: "Do I Wanna Know?", artist: "Arctic Monkeys", genre: "indie" },
  { id: "track_046", title: "About You", artist: "The 1975", genre: "indie" },
  { id: "track_047", title: "Electric Feel", artist: "MGMT", genre: "indie" },
  { id: "track_048", title: "Holocene", artist: "Bon Iver", genre: "folk" },
  { id: "track_049", title: "White Winter Hymnal", artist: "Fleet Foxes", genre: "folk" },
  { id: "track_050", title: "The Night We Met", artist: "Lord Huron", genre: "folk" },
  { id: "track_051", title: "Everlong", artist: "Foo Fighters", genre: "rock" },
  { id: "track_052", title: "Seven Nation Army", artist: "The White Stripes", genre: "rock" },
  { id: "track_053", title: "Mr. Brightside", artist: "The Killers", genre: "rock" },
  { id: "track_054", title: "Don't Stop Me Now", artist: "Queen", genre: "rock" },
  { id: "track_055", title: "So What", artist: "Miles Davis", genre: "jazz" },
  { id: "track_056", title: "Blue in Green", artist: "Miles Davis", genre: "jazz" },
  { id: "track_057", title: "Take Five", artist: "The Dave Brubeck Quartet", genre: "jazz" },
  { id: "track_058", title: "My Favorite Things", artist: "John Coltrane", genre: "jazz" },
  { id: "track_059", title: "Teardrop", artist: "Massive Attack", genre: "electronic" },
  { id: "track_060", title: "Midnight City", artist: "M83", genre: "electronic" },
];

const MOODS = ["happy", "sad", "excited", "bored", "calm", "energetic", "focused"];
const ACTIVITIES = ["study", "work", "party", "relax", "workout", "commute"];
const GENRES = ["lo-fi", "ambient", "electronic", "dance", "indie", "folk", "rock", "jazz"];
const REAL_WORLD_FROM = 33;

const form = document.getElementById("recommend-form");
const trackList = document.getElementById("track-list");
const moodSelect = document.getElementById("mood");
const activitySelect = document.getElementById("activity");
const genreSelect = document.getElementById("genre");
const avoidArtists = document.getElementById("avoid-artists");
const apiBaseInput = document.getElementById("api-base");
const statusEl = document.getElementById("status");
const resultEl = document.getElementById("result");
const submitBtn = document.getElementById("submit-btn");
const catalogueMeta = document.getElementById("catalogue-meta");
const filterButtons = document.querySelectorAll("[data-filter]");

let catalogue = FALLBACK_CATALOGUE.slice();
let activeFilter = "real";

function fillSelect(select, values) {
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  }
}

function trackOrdinal(trackId) {
  const match = /^track_(\d+)$/.exec(trackId);
  return match ? Number(match[1]) : 0;
}

function isRealWorld(track) {
  return trackOrdinal(track.id) >= REAL_WORLD_FROM;
}

function filteredCatalogue() {
  if (activeFilter === "real") {
    return catalogue.filter(isRealWorld);
  }
  if (activeFilter === "demo") {
    return catalogue.filter((track) => !isRealWorld(track));
  }
  return catalogue;
}

function renderTrackList() {
  const selected = new Set(selectedTrackIds());
  const tracks = filteredCatalogue();
  trackList.innerHTML = "";

  if (!tracks.length) {
    const empty = document.createElement("p");
    empty.className = "hint";
    empty.textContent = "No tracks in this filter.";
    trackList.appendChild(empty);
    return;
  }

  for (const track of tracks) {
    const label = document.createElement("label");
    label.className = "track-option";
    if (isRealWorld(track)) {
      label.classList.add("is-real");
    }
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "recent_tracks";
    checkbox.value = track.id;
    checkbox.checked = selected.has(track.id);
    const text = document.createElement("span");
    const badge = isRealWorld(track)
      ? `<span class="badge">real</span>`
      : `<span class="badge badge-muted">fixture</span>`;
    text.innerHTML = `${escapeHtml(track.title)} — ${escapeHtml(track.artist)} (${escapeHtml(
      track.genre
    )}) ${badge}`;
    label.append(checkbox, text);
    trackList.appendChild(label);
  }
}

function selectedTrackIds() {
  return Array.from(
    form.querySelectorAll('input[name="recent_tracks"]:checked'),
    (input) => input.value
  );
}

function showStatus(message, isError = false) {
  statusEl.hidden = false;
  statusEl.textContent = message;
  statusEl.dataset.tone = isError ? "error" : "info";
}

function hideStatus() {
  statusEl.hidden = true;
  statusEl.textContent = "";
  delete statusEl.dataset.tone;
}

function showResult(payload) {
  const track = payload.recommended_track;
  const moods = (track.moods || []).map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("");
  const activities = (track.activities || [])
    .map((item) => `<span class="tag">${escapeHtml(item)}</span>`)
    .join("");
  const score =
    typeof payload.score === "number" ? payload.score.toFixed(2) : String(payload.score);
  const realNote = isRealWorld(track)
    ? `<p class="track-note">Curated real recording from the expanded catalogue.</p>`
    : `<p class="track-note">Synthetic demo fixture used for controlled evaluation.</p>`;

  resultEl.hidden = false;
  resultEl.innerHTML = `
    <h2>Recommendation</h2>
    <p class="track-title">${escapeHtml(track.title)}</p>
    <p class="track-meta">${escapeHtml(track.artist)} · ${escapeHtml(track.genre)}</p>
    <p class="track-id">id: ${escapeHtml(track.id)}</p>
    ${realNote}
    <div class="score-row">
      <span class="score-label">Score</span>
      <span class="score-value">${escapeHtml(score)}</span>
    </div>
    <p class="reason">${escapeHtml(payload.reason || "")}</p>
    <div class="tags">${moods}${activities}</div>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function buildBody() {
  const recentTracks = selectedTrackIds();
  const mood = moodSelect.value || null;
  const activity = activitySelect.value || null;
  const genre = genreSelect.value || null;

  if (!recentTracks.length && !mood && !activity && !genre) {
    throw new Error("Choose at least one recent track or a mood, activity, or genre.");
  }

  return {
    recent_tracks: recentTracks,
    mood,
    activity,
    genre,
    avoid_repeated_artists: avoidArtists.checked,
  };
}

function apiBase() {
  return apiBaseInput.value.replace(/\/$/, "");
}

async function loadCatalogue() {
  catalogueMeta.textContent = "Loading catalogue…";
  try {
    const response = await fetch(`${apiBase()}/catalogue`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    const payload = await response.json();
    if (!Array.isArray(payload.tracks) || !payload.tracks.length) {
      throw new Error("Empty catalogue");
    }
    catalogue = payload.tracks;
    const realCount = catalogue.filter(isRealWorld).length;
    catalogueMeta.textContent = `${catalogue.length} tracks loaded from API · ${realCount} curated real recordings`;
  } catch {
    catalogue = FALLBACK_CATALOGUE.slice();
    const realCount = catalogue.filter(isRealWorld).length;
    catalogueMeta.textContent = `Using embedded fallback (${catalogue.length} tracks, ${realCount} real). Start the API for live catalogue.`;
  }
  renderTrackList();
}

async function onSubmit(event) {
  event.preventDefault();
  hideStatus();
  resultEl.hidden = true;

  let body;
  try {
    body = buildBody();
  } catch (error) {
    showStatus(error.message, true);
    return;
  }

  submitBtn.disabled = true;
  showStatus("Calling NextTrack…");

  try {
    const response = await fetch(`${apiBase()}/recommend`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail =
        typeof payload.detail === "string"
          ? payload.detail
          : JSON.stringify(payload.detail || payload);
      throw new Error(`${response.status}: ${detail}`);
    }
    hideStatus();
    showResult(payload);
  } catch (error) {
    showStatus(error.message || "Request failed", true);
  } finally {
    submitBtn.disabled = false;
  }
}

fillSelect(moodSelect, MOODS);
fillSelect(activitySelect, ACTIVITIES);
fillSelect(genreSelect, GENRES);

for (const button of filterButtons) {
  button.addEventListener("click", () => {
    activeFilter = button.dataset.filter;
    for (const other of filterButtons) {
      other.setAttribute("aria-pressed", String(other === button));
    }
    renderTrackList();
  });
}

form.addEventListener("submit", onSubmit);
apiBaseInput.addEventListener("change", () => {
  loadCatalogue();
});

loadCatalogue();
