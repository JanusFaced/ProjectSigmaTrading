// Это как print() в Python
console.log("Hello from JavaScript!");

// Переменные и типы данных (как в Python)
const name = "Docker";
let count = 42;

console.log(`Hello, ${name}! You are visitor number ${count}`);

// Функция (как def в Python)
function add(a, b) {
    return a + b;
}

const result = add(5, 3);
console.log(`5 + 3 = ${result}`);

// Работа с массивом (как list в Python)
const fruits = ["apple", "banana", "orange"];
fruits.forEach((fruit, index) => {
    console.log(`${index + 1}. ${fruit}`);
});

// Асинхронность (как async/await в Python)
async function waitAndSay() {
    console.log("Ждем 2 секунды...");
    await new Promise(resolve => setTimeout(resolve, 2000));
    console.log("Прошло 2 секунды!");
}

// Запускаем асинхронную функцию
waitAndSay();

console.log("Этот код выполнится до ожидания, как в Python с asyncio.create_task()");