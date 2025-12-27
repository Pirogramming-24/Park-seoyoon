let answer_num = [];     // 정답 3개
let attempts = 9;        // 남은 횟수
let gameOver = false;    

let attemptsE, num1, num2, num3, submit_btn, resultsEl, resultimg;

// 전체 초기화
window.onload = function () {
    attemptsE = document.getElementById("attempts");
    num1 = document.getElementById("number1");
    num2 = document.getElementById("number2");
    num3 = document.getElementById("number3");

    submit_btn = document.querySelector(".submit-button");
    resultsEl = document.getElementById("results");
    resultimg = document.getElementById("game-result-img");

    initGame();
};

//랜덤 생성
function makeRandomNumber() {
    const nums = [];
    while (nums.length < 3) {
        const n = Math.floor(Math.random() * 10);
        if (!nums.includes(n)) nums.push(n);
    }
    return nums;
}

// input 비우기
function clearInputs() {
    num1.value = "";
    num2.value = "";
    num3.value = "";
    num1.focus();
}

// 게임 전체 초기화
function initGame() {
    answer_num = makeRandomNumber();
    attempts = 9;
    gameOver = false;

    attemptsE.textContent = attempts;
    resultsEl.innerHTML = "";
    resultimg.src = "";

    submit_btn.disabled = false;
    clearInputs();

}

// 결과 1줄 출력
function displayResult(inputArr, strike, ball) {
    const row = document.createElement("div");
    row.className = "check-result";

    const left = document.createElement("div");
    left.className = "left";
    left.textContent = inputArr.join("");

    const colon = document.createElement("div");
    colon.textContent = ":";

    const right = document.createElement("div");
    right.className = "right";

  //  아웃: strike, ball 둘 다 0일 때는 O만
    if (strike === 0 && ball === 0) {
        const outBadge = document.createElement("span");
        outBadge.className = "num-result out";
        outBadge.textContent = "O";
        right.appendChild(outBadge);
    } 
        else {
    if (strike > 0) {
        const sBadge = document.createElement("span");
        sBadge.className = "num-result strike";
        sBadge.textContent = `${strike}S`;
        right.appendChild(sBadge);
    }

    if (ball > 0) {
        const bBadge = document.createElement("span");
        bBadge.className = "num-result ball";
        bBadge.textContent = `${ball}B`;
        right.appendChild(bBadge);
    }
    }

    row.appendChild(left);
    row.appendChild(colon);
    row.appendChild(right);
    resultsEl.appendChild(row);
}



function check_numbers() {
    if (gameOver) return;

    const v1 = num1.value;
    const v2 = num2.value;
    const v3 = num3.value;

  // 빈 값 있으면 input만 초기화
    if (v1 === "" || v2 === "" || v3 === "") {
        clearInputs();
        return;
    }

    const inputArr = [Number(v1), Number(v2), Number(v3)];


    let strike = 0;
    let ball = 0;

    for (let i = 0; i < 3; i++) {
        if (inputArr[i] === answer_num[i]) {
            strike++;
        } else if (answer_num.includes(inputArr[i])) {
        ball++;
        }
    }

  // 3) 결과 출력 (nS nB 또는 O)
    displayResult(inputArr, strike, ball);

  // 4) 횟수 차감
    attempts--;
    attemptsE.textContent = attempts;

  // 5) 종료 조건 처리 + 이미지 출력 + 버튼 비활성화
    if (strike === 3) {
        resultimg.src = "success.png";
        submit_btn.disabled = true;
        gameOver = true;
        return;
    }

    if (attempts === 0) {
        resultimg.src = "fail.png";
        submit_btn.disabled = true;
        gameOver = true;
        return;
    }

    clearInputs();
}

