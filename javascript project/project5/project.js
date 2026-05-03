const getinput = document.getElementById("guessInput");

function checkGuess() {
  const userGuess = parseInt(getinput.value);
  const randomNumber = Math.floor(Math.random() * 100) + 1;
  if (userGuess === randomNumber) {
    alert("Congratulations! You guessed the correct number: " + randomNumber);
  } else if (userGuess < randomNumber) {
    alert("Too low! The correct number was: " + randomNumber);
  } else {
    alert("Too high! The correct number was: " + randomNumber);
  }
}

document.getElementById("submitbutton").addEventListener("click", checkGuess);
