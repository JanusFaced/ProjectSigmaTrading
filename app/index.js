import axios from 'axios';

async function main() {

	await checkMultipleSites();
	console.log("✅ Все проверки завершены!");

	//var result = testCode()
	//console.log(`code exit = ${result}`)

}

async function checkMultipleSites() {
	const sites = [
		{ url: 'https://google.com', name: 'Google' },
		{ url: 'https://github.com', name: 'GitHub' },
		{ url: 'https://nonexistent-site-12345.com', name: 'Несуществующий сайт' },
		{ url: 'https://ya.ru', name: 'Яндекс' }
	];
	
	const promises = sites.map(site => checkWebsite(site.url, site.name));
	await Promise.all(promises);
}

async function checkWebsite(url, name) {
	try {
		const startTime = Date.now();
		const response = await axios.get(url, { timeout: 5000 });
		const endTime = Date.now();
		const pingTime = endTime - startTime;
		
		console.log(`✅ ${name} (${url})`);
		console.log(`   Статус: ${response.status} OK`);
		console.log(`   Время ответа: ${pingTime} мс\n`);
	} catch (error) {
		console.log(`❌ ${name} (${url}) | Ошибка: ${error.message}\n`);
	}
}

function testCode() {

	console.log("Start main!");

	var varA = 101;
	let count = 0;
	const name = "Docker";

	count += 1
	console.log(` > ${count} : Hello, ${name}! You are visitor number ${varA}`);

	const result = add(5, 3);

	count += 1
	console.log(` > ${count} : 5 + 3 = ${result}`);

	const fruits = ["apple", "banana", "orange", "watermelon", "cucumber", "potato"];
	fruits.forEach((fruit, index) => {
		count += 1
		console.log(` > ${count} : ${index + 1}. ${fruit}`);
	});

	waitAndSay();

	count += 1
	console.log(` > ${count} : Этот код выполнится до завершения асинхронной функции, как в Python с asyncio.create_task()`);

	return 0;

}

function add(a, b) {
	return a + b;
}

async function waitAndSay() {
	console.log("Ждем 2 секунды...");
	await new Promise(resolve => setTimeout(resolve, 2000));
	console.log("Прошло 2 секунды!");
}

main().catch(error => {
	console.error(`❌ Критическая ошибка: ${error.message}`);
});



