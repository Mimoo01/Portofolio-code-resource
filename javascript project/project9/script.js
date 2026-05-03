let playlist = JSON.parse(localStorage.getItem("playlist"));
// ambil element id
const audio = document.getElementById("audio");
const playPauseButton = document.getElementById("play-pause");
const pauseIcon = document.getElementById("play-icon");
const progressBar = document.getElementById("progress-bar");
const playlistElement = document.getElementById("playlist");
const audioUpload = document.getElementById("current-track");

// fungsi buat list audio
function createPlaylist() {
  playlistElement.innerHTML = "";
  playlist.forEach((track, index) => {
    const li = document.createElement("li");
    li.textContent = track.title;
    li.dataset.src = track.src;

    li.addEventListener("click", () => {
      audio.src = track.src;
      audio.play();
      updatePlayPauseIcon();

      document.querySelectorAll("#playlist li").forEach((item) => item.classList.remove("active"));

      li.classList.add("active");

      currentTrack.textContent = track.title;
    });

    playlistElement.appendChild(li);
  });
}

function updatePlayPauseIcon() {
  if (audio.paused) {
    playIcon.style.display = "block";
    pauseIcon.style.display = "none";
  } else {
    playIcon.style.display = "none";
    pauseIcon.style.display = "block";
  }
}

function savePlaylist() {
  localStorage.setItem("playlist");
}

createPlaylist();

audioUpload.addEventListener("change", (event) => {
  const files = Array.from(event.target.files);
  files.forEach((file) => {
    const reader = new FileReader();
    reader.onload = function (e) {
      const track = {
        title: file.name,
        src: e.target.result,
      };
      playlist.push(track);
      createPlaylist();
      savePlaylist();
    };
    reader.readAsDataUrl(file);
  });
});
