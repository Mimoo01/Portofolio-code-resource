// get element from the DOM
const canvas = document.getElementById("canvas");
const ctx = canvas.getContext("2d");

const brushBtn = document.getElementById("brush");
const eraserBtn = document.getElementById("eraser");
const clearBtn = document.getElementById("clear");
const colorPicker = document.getElementById("colorPicker");

// set ukuran dari canvas
canvas.width = 800;
canvas.height = 600;

// variabel untuk menyimpan status alat
let painting = false;
let erasing = false;
let currentColor = "#000000";
let lineWidth = 5;

function startPosition(e) {
  painting = true;
  draw(e);
}

// function to stop painting
function endPosition(e) {
  painting = false;
  ctx.beginPath();
}

// function buat gambar di canvas
function draw(e) {
  if (!painting) return;

  ctx.lineWidth = lineWidth;
  ctx.lineCap = "round";

  ctx.strokeStyle = erasing ? "#FFFFFF" : currentColor;

  ctx.lineTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);

  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(e.clientX - canvas.offsetLeft, e.clientY - canvas.offsetTop);
}

function selectBrush() {
  erasing = false;
  brushBtn.classList.add("active");
  eraserBtn.classList.remove("active");
}

function selectEraser() {
  erasing = true;
  eraserBtn.classList.add("active");
  brushBtn.classList.remove("active");
}

function clearCanvas() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function changeColor(e) {
  currentColor = e.target.value;
}

// add event listener to each tool
brushBtn.addEventListener("click", selectBrush);
eraserBtn.addEventListener("click", selectEraser);
clearBtn.addEventListener("click", clearCanvas);
colorPicker.addEventListener("change", changeColor);

canvas.addEventListener("mousedown", startPosition);
canvas.addEventListener("mouseup", endPosition);
canvas.addEventListener("mousemove", draw);
