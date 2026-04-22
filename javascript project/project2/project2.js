// Getting html elementnya
const countdownElement = document.getElementById("countdown");
const daysElement = document.getElementById("days");
const hoursElement = document.getElementById("hours");
const minutesElement = document.getElementById("minutes");
const secondsElement = document.getElementById("seconds");

const inputHours = document.getElementById("inputHours");
const inputMinutes = document.getElementById("inputMinutes");
const inputSeconds = document.getElementById("inputSeconds");
const startButton = document.getElementById("startButton");
const resetButton = document.getElementById("resetButton");

let countdownInterval;

// Function to startTimer
function startTimer() {
  let hours = parseInt(inputHours.value) || 0;
  let minutes = parseInt(inputMinutes.value) || 0;
  let seconds = parseInt(inputSeconds.value) || 0;

  //   convert the total time into seconds
  let totalTimeInSeconds = hours * 3600 + minutes * 60 + seconds;

  //   if no time is input, stop the function
  if (totalTimeInSeconds <= 0) {
    alert("Please enter a valid time.");
    return;
  }
  // clear the input after timer start
  inputHours.value = "";
  inputMinutes.value = "";
  inputSeconds.value = "";
  // function to update the time diplay ever second
  countdownInterval = setInterval(() => {
    // calculate remaining time start
    const days = Math.floor(totalTimeInSeconds / (3600 * 24));
    const hours = Math.floor((totalTimeInSeconds % (3600 * 24)) / 3600);
    const minutes = Math.floor((totalTimeInSeconds % 3600) / 60);
    const seconds = totalTimeInSeconds % 60;

    daysElement.textContent = String(days).padStart(2, "0");
    hoursElement.textContent = String(hours).padStart(2, "0");
    minutesElement.textContent = String(minutes).padStart(2, "0");
    secondsElement.textContent = String(seconds).padStart(2, "0");

    // Decrease the total time by 1 second
    totalTimeInSeconds--;

    // If time is up, stop the timer and show alert
    if (totalTimeInSeconds < 0) {
      clearInterval(countdownInterval);
      alert("Time's up!");
    }
  }, 1000);
}

// add event listener to start button
startButton.addEventListener("click", () => {
  clearInterval(countdownInterval); // Clear any existing timer
  startTimer();
});
