const canvas = document.getElementById('snakeCanvas');
const ctx = canvas.getContext('2d');
const scoreDisplay = document.getElementById('currentScore');
const highScoreDisplay = document.getElementById('highScore');
const startBtn = document.getElementById('startBtn');

// Set canvas size
const GRID_SIZE = 20;
const TILE_COUNT = 20;
canvas.width = GRID_SIZE * TILE_COUNT;
canvas.height = GRID_SIZE * TILE_COUNT;

let snake = [{x: 10, y: 10}];
let food = {x: 5, y: 5};
let dx = 0;
let dy = 0;
let score = 0;
let highScore = localStorage.getItem('snakeHighScore') || 0;
let gameLoop;
let isRunning = false;

highScoreDisplay.textContent = highScore.toString().padStart(3, '0');

function draw() {
    // Clear canvas
    ctx.fillStyle = '#000';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Draw Grid (Subtle)
    ctx.strokeStyle = '#111';
    ctx.lineWidth = 0.5;
    for(let i=0; i<canvas.width; i+=GRID_SIZE) {
        ctx.beginPath(); ctx.moveTo(i, 0); ctx.lineTo(i, canvas.height); ctx.stroke();
        ctx.beginPath(); ctx.moveTo(0, i); ctx.lineTo(canvas.width, i); ctx.stroke();
    }

    // Move Snake
    const head = {x: snake[0].x + dx, y: snake[0].y + dy};
    
    // Check collisions
    if (head.x < 0 || head.x >= TILE_COUNT || head.y < 0 || head.y >= TILE_COUNT || collision(head)) {
        gameOver();
        return;
    }

    snake.unshift(head);
    
    // Check food
    if (head.x === food.x && head.y === food.y) {
        score += 10;
        scoreDisplay.textContent = score.toString().padStart(3, '0');
        generateFood();
    } else {
        if (dx !== 0 || dy !== 0) snake.pop();
    }

    // Draw Food
    ctx.shadowBlur = 15;
    ctx.shadowColor = '#0df';
    ctx.fillStyle = '#0df';
    ctx.fillRect(food.x * GRID_SIZE + 2, food.y * GRID_SIZE + 2, GRID_SIZE - 4, GRID_SIZE - 4);

    // Draw Snake
    snake.forEach((part, index) => {
        const alpha = 1 - (index / snake.length) * 0.6;
        ctx.shadowBlur = index === 0 ? 20 : 10;
        ctx.shadowColor = '#ff3366';
        ctx.fillStyle = `rgba(255, 51, 102, ${alpha})`;
        ctx.fillRect(part.x * GRID_SIZE + 1, part.y * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2);
    });
    ctx.shadowBlur = 0;
}

function collision(head) {
    return snake.some((part, index) => index !== 0 && part.x === head.x && part.y === head.y);
}

function generateFood() {
    food = {
        x: Math.floor(Math.random() * TILE_COUNT),
        y: Math.floor(Math.random() * TILE_COUNT)
    };
    // Ensure food doesn't spawn on snake
    if (snake.some(p => p.x === food.x && p.y === food.y)) generateFood();
}

function gameOver() {
    clearInterval(gameLoop);
    isRunning = false;
    startBtn.textContent = 'RESTART SYSTEM';
    if (score > highScore) {
        highScore = score;
        localStorage.setItem('snakeHighScore', highScore);
        highScoreDisplay.textContent = highScore.toString().padStart(3, '0');
    }
    
    ctx.fillStyle = 'rgba(0,0,0,0.75)';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.fillStyle = '#ff3366';
    ctx.font = 'bold 30px Inter';
    ctx.textAlign = 'center';
    ctx.fillText('CORE COLLAPSED', canvas.width/2, canvas.height/2);
    ctx.font = '16px JetBrains Mono';
    ctx.fillStyle = '#fff';
    ctx.fillText(`FINAL SCORE: ${score}`, canvas.width/2, canvas.height/2 + 40);
}

function startGame() {
    if (isRunning) return;
    snake = [{x: 10, y: 10}];
    dx = 1; dy = 0;
    score = 0;
    scoreDisplay.textContent = '000';
    generateFood();
    isRunning = true;
    startBtn.textContent = 'GAME RUNNING...';
    gameLoop = setInterval(draw, 100);
}

// Controller
window.addEventListener('keydown', e => {
    switch(e.key) {
        case 'ArrowUp': if (dy === 0) { dx = 0; dy = -1; } break;
        case 'ArrowDown': if (dy === 0) { dx = 0; dy = 1; } break;
        case 'ArrowLeft': if (dx === 0) { dx = -1; dy = 0; } break;
        case 'ArrowRight': if (dx === 0) { dx = 1; dy = 0; } break;
    }
});

startBtn.addEventListener('click', startGame);

// Initial Frame
draw();

// Tab Switcher Logic
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
        
        btn.classList.add('active');
        const targetId = btn.getAttribute('data-tab') + 'Tab';
        document.getElementById(targetId).classList.add('active');
        
        // Pause game if switching away
        if (btn.getAttribute('data-tab') !== 'arcade' && isRunning) {
            clearInterval(gameLoop);
            isRunning = false;
            startBtn.textContent = 'RESUME GAME';
        }
    });
});
