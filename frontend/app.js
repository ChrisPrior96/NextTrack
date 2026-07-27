const CATALOGUE = [
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
];

const MOODS = ["happy", "sad", "excited", "bored", "calm", "energetic", "focused"];
const ACTIVITIES = ["study", "work", "party", "relax", "workout", "commute"];
const GENRES = ["lo-fi", "ambient", "electronic", "dance", "indie", "folk", "rock", "jazz"];

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

function fillSelect(select, values) {
  for (const value of values) {
    const option = document.createElement("option");
    option.value = value;
    option.textContent = value;
    select.appendChild(option);
  }
}

function renderTrackList() {
  trackList.innerHTML = "";
  for (const track of CATALOGUE) {
    const label = document.createElement("label");
    label.className = "track-option";
    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.name = "recent_tracks";
    checkbox.value = track.id;
    const text = document.createElement("span");
    text.textContent = `${track.title} — ${track.artist} (${track.genre})`;
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
}

function showResult(payload) {
  const track = payload.recommended_track;
  resultEl.hidden = false;
  resultEl.innerHTML = `
    <h2>Recommendation</h2>
    <p class="track-title">${escapeHtml(track.title)}</p>
    <p class="track-meta">${escapeHtml(track.artist)} · ${escapeHtml(track.genre)}</p>
    <p class="track-id">id: ${escapeHtml(track.id)}</p>
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

  const base = apiBaseInput.value.replace(/\/$/, "");
  submitBtn.disabled = true;
  showStatus("Calling NextTrack…");

  try {
    const response = await fetch(`${base}/recommend`, {
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
renderTrackList();
form.addEventListener("submit", onSubmit);
