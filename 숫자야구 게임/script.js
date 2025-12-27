var answer = [];        // 정답 3자리 
var attempts = 9;       // 남은 횟수
var gameOver = false;   // 게임 종료 여부

// HTML 요소
var input1, input2, input3;
var resultsBox, attemptsText, resultImg, submitBtn;

// 0~9 랜덤 값 3개 만들기
function makeAnswer() {
  var nums = [];
  while (nums.length < 3) {
    var n = Math.floor(Math.random() * 10);
    if (nums.indexOf(n) === -1) nums.push(n);
  }
  return nums;
}

// 입력칸 비우기
function clearInputs() {
  input1.value = "";
  input2.value = "";
  input3.value = "";
  input1.focus();
}

// 결과창 비우기
function clearResults() {
  resultsBox.innerHTML = "";
}

// 이미지 숨기기
function hideImage() {
  resultImg.src = "";
  resultImg.style.display = "none";
}

// 이미지 보여주기
function showImage(filename) {
  resultImg.src = filename; // success.png / fail.png
  resultImg.style.display = "block";
}

// 남은 횟수 표시 업데이트
function updateAttemptsText() {
  attemptsText.textContent = attempts;
}

// 버튼 비활성화
function disableGame() {
  gameOver = true;
  submitBtn.disabled = true;
  input1.disabled = true;
  input2.disabled = true;
  input3.disabled = true;
}

// 게임 초기화
function initGame() {
  answer = makeAnswer();
  attempts = 9;
  gameOver = false;

  clearInputs();
  clearResults();
  hideImage();

  submitBtn.disabled = false;
  input1.disabled = false;
  input2.disabled = false;
  input3.disabled = false;

  updateAttemptsText();
}

// strike/ball 계산 (중복 입력도 안전하게 처리)
function getStrikeBall(guess) {
  var strike = 0;
  var ball = 0;

  // 정답/입력에서 이미 사용한 자리 체크
  var usedAnswer = [false, false, false];
  var usedGuess = [false, false, false];

  // 1) 스트라이크 먼저 계산
  for (var i = 0; i < 3; i++) {
    if (guess[i] === answer[i]) {
      strike++;
      usedAnswer[i] = true;
      usedGuess[i] = true;
    }
  }

  // 2) 볼 계산
  for (var g = 0; g < 3; g++) {
    if (usedGuess[g]) continue;

    for (var a = 0; a < 3; a++) {
      if (usedAnswer[a]) continue;

      if (guess[g] === answer[a]) {
        ball++;
        usedAnswer[a] = true;
        usedGuess[g] = true;
        break;
      }
    }
  }

  return { strike: strike, ball: ball };
}

// 한 줄 결과 
function addResultLine(guess, strike, ball) {
  var row = document.createElement("div");
  row.className = "check-result";

  var left = document.createElement("div");
  left.className = "left";

  for (var i = 0; i < 3; i++) {
    var sp = document.createElement("span");
    sp.className = "num-result";

    // 각 자리 색칠: strike / ball / out
    if (guess[i] === answer[i]) {
      sp.className += " strike";
    } else if (answer.indexOf(guess[i]) !== -1) {
      sp.className += " ball";
    } else {
      sp.className += " out";
    }

    sp.textContent = guess[i];
    left.appendChild(sp);
    left.appendChild(document.createTextNode(" "));
  }

  var right = document.createElement("div");
  right.className = "right";

  var resultSpan = document.createElement("span");

  // 결과 텍스트
  if (strike === 0 && ball === 0) {
    resultSpan.textContent = "O";
    resultSpan.className = "out";
  } else {
    resultSpan.textContent = strike + " S " + ball + " B";
    // 보기 좋게 대표 색 하나만 줌 (strike 있으면 strike, 없으면 ball)
    if (strike > 0) resultSpan.className = "strike";
    else resultSpan.className = "ball";
  }

  right.appendChild(resultSpan);

  row.appendChild(left);
  row.appendChild(right);

  resultsBox.appendChild(row);
}

// 버튼 onclick으로 연결된 함수 (필수)
function check_numbers() {
  if (gameOver) return;

  // 1) 하나라도 비었으면: 확인하지 않고 입력만 비움
  if (input1.value === "" || input2.value === "" || input3.value === "") {
    clearInputs();
    return;
  }

  // 입력값 읽기 (0~9만 들어온다고 가정)
  var guess = [
    parseInt(input1.value, 10),
    parseInt(input2.value, 10),
    parseInt(input3.value, 10)
  ];

  // 2) 시도 횟수 감소 (3개 입력된 경우에만)
  attempts--;
  updateAttemptsText();

  // 3) 결과 계산
  var r = getStrikeBall(guess);

  // 4) 화면 업데이트
  addResultLine(guess, r.strike, r.ball);
  clearInputs();

  // 5) 승/패 처리
  if (r.strike === 3) {
    showImage("success.png");
    disableGame();
    return;
  }

  if (attempts <= 0) {
    showImage("fail.png");
    disableGame();
    return;
  }
}

// 페이지 초기화
document.addEventListener("DOMContentLoaded", function () {
  input1 = document.getElementById("number1");
  input2 = document.getElementById("number2");
  input3 = document.getElementById("number3");

  resultsBox = document.getElementById("results");
  attemptsText = document.getElementById("attempts");
  resultImg = document.getElementById("game-result-img");

  // 
  submitBtn = document.querySelector(".submit-button");

  initGame();
});


window.check_numbers = check_numbers;
