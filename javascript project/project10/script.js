// Ambil element html yang diperluan

const textTotypeElement = document.getElementById("text-to-type");
const textToType = textTotypeElement.innerHTML.split("");
const userInput = document.getElementById("user-input");
const startButton = document.getElementById("start-button");
const timeDisplay = document.getElementById("time");
const wpmDisplay = document.getElementById("words-per-minute");

let startTime;
let timerInterval;

function startTest() {
  startTime = new Date();
  userInput.value = "";
  userInput.focus();
  timerInterval = setInterval(updateTimer, 1000);
  textTotypeElement.innerHTML = textToType.map((word) => `<span>${word}</span>`).join("");
}

function updateTimer() {
  const currentTime = new Date();
  const elapsedTime = Math.floor((currentTime - startTime) / 1000);
  timeDisplay.innerText = elapsedTime;
}

function calculateWPM() {
  const wordsTyped = userInput.value.trim().split(/\s+/).length;
  const elapsedTime = Math.floor((new Date() - startTime) / 1000);
  const minutes = elapsedTime / 60;
  const wpm = Math.floor(wordsTyped / minutes);
  wpmDisplay.innerHTML = wpm;
}

// startTest();

function checkInput() {
  const typedText = userInput.value.trim().split("");
  const spans = textTotypeElement.querySelectorAll("span");

  // menngecek yang diketik oleh user

  typedText.forEach((word, index) => {
    if (spans[index]) {
      console.log(spans[index], word);
      if (word === textToType[index]) {
        spans[index].className = "correct";
      } else {
        spans[index].className = "incorrect";
      }
    }
  });

  // handle function buat user nya menghapus text yang sudah diketik sebelumnya

  for (let i = typedText.length; i < spans.length; i++) {
    spans[i].className = "";
  }
}

startButton.addEventListener("click", () => {
  startTest();
});

function stopTest() {
  clearInterval(timerInterval);
  calculateWPM();
}

userInput.addEventListener("input", () => {
  checkInput();
  const typedText = userInput.value;
  if (typedText.trim() === textToType.join("")) {
    stopTest();
  }
});
