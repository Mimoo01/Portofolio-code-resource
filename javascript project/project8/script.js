const question = [
  {
    question: "What is JavaScript?",
    answer: [
      { text: "A programming language", isCorrect: true },
      { text: "A type of coffee", isCorrect: false },
      { text: "A brand of shoes", isCorrect: false },
      { text: "A musical instrument", isCorrect: false },
    ],
  },
  {
    question: "Which company developed JavaScript?",
    answer: [
      { text: "Microsoft", isCorrect: false },
      { text: "Netscape", isCorrect: true },
      { text: "Google", isCorrect: false },
      { text: "Apple", isCorrect: false },
    ],
  },
  {
    question: "What is the correct syntax for referring to an external script called 'script.js'?",
    answer: [
      { text: "<script src='script.js'>", isCorrect: true },
      { text: "<script href='script.js'>", isCorrect: false },
      { text: "<script name='script.js'>", isCorrect: false },
      { text: "<script type='text/javascript'>", isCorrect: false },
    ],
  },
];

let currentQuestionIndex = 0;
let score = 0;

// ambil semua element yang dibutuhkan

const questionContainer = document.getElementById("question-container");
const questionElement = document.getElementById("question-text");
const answerButtons = document.getElementById("answer-buttons");
const nextButton = document.getElementById("next-question-btn");
const resultContainer = document.getElementById("result-container");
const scoreElement = document.getElementById("score");
const restartButton = document.getElementById("restart-btn");

function startQuiz() {
  currentQuestionIndex = 0;
  score = 0;
  nextButton.style.display = "none";
  resultContainer.style.display = "none";
  questionContainer.style.display = "block";

  // function untuk menampilkan question
  showQuestion();
}

function showQuestion() {
  // untuk mereset state
  resetState();

  const currentQuestion = question[currentQuestionIndex];
  questionElement.textContent = currentQuestion.question;

  //   buat button untuk jawaban secara dinamis
  currentQuestion.answer.forEach((answer) => {
    const button = document.createElement("button");
    button.textContent = answer.text;
    button.classList.add("answer-btn");
    if (answer.isCorrect) {
      button.dataset.correct = answer.isCorrect;
    }
    button.addEventListener("click", selectAnswer);
    answerButtons.appendChild(button);
  });
}

// startQuiz();

function resetState() {
  nextButton.style.display = "none";
  while (answerButtons.firstChild) {
    answerButtons.removeChild(answerButtons.firstChild);
  }
}

function selectAnswer(e) {
  const selectedButton = e.target;
  const isCorrect = selectedButton.dataset.correct === "true";

  if (isCorrect) {
    selectedButton.style.backgroundColor = "green";
    score++;
  } else {
    selectedButton.style.backgroundColor = "red";
  }

  Array.from(answerButtons.children).forEach((button) => {
    button.disabled = true;
    if (button.dataset.correct === "true") {
      button.style.backgroundColor = "green";
    }
  });

  if (currentQuestionIndex < question.length - 1) {
    nextButton.style.display = "inline-block";
  } else {
    showResult();
  }
}

restartButton.addEventListener("click", startQuiz);

// disable all button after select answer

startQuiz();

nextButton.addEventListener("click", () => {
  currentQuestionIndex++;
  showQuestion();
});

function showResult() {
  questionContainer.style.display = "none";
  resultContainer.style.display = "block";
  scoreElement.textContent = `Your Score: ${score} / ${question.length}`;
}

//
