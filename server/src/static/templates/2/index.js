const start = document.querySelector("#start")
const begin = document.querySelector("#begin")
const game = document.querySelector("#game")
const bg1 = document.querySelector('.bg1');
const bg2 = document.querySelector('.bg2');
const myplane = document.querySelector('.myplane');
const myplane_speed = 5;
const bullet_speed = 10;
const bg_speed = 1;
const enemy_speed = 5;
// 创建一个数组来存储敌机的图片
const enemyTypes = [
    { image: 'enemy1.png', boomImage: 'enemy1b.gif', width: '34px', height: '24px', speed: 3, health: 3, probability: 0.6 }, // 小敌机
    { image: 'enemy2.png', boomImage: 'enemy2b.gif', width: '46px', height: '60px', speed: 2, health: 5, probability: 0.3 }, // 中敌机
    { image: 'enemy3.png', boomImage: 'enemy3b.gif', width: '110px', height: '164px', speed: 1, health: 7, probability: 0.1 }  // 大敌机
];

// 背景动画
function animateBackground() {
    bg1.style.top = bg1.offsetTop + bg_speed + 'px';
    bg2.style.top = bg2.offsetTop + bg_speed + 'px';
    if (bg1.offsetTop >= 680) {
        bg1.style.top = '-680px';
    }
    if (bg2.offsetTop >= 680) {
        bg2.style.top = '-680px';
    }

    let enemies = document.querySelectorAll('.enemy');
    let plane = document.querySelector('.myplane');
    const auto_img = document.querySelector('.auto-img');
    for (let i = 0; i < enemies.length; i++) {
        let enemy = enemies[i];
        let enemyRect = enemy.getBoundingClientRect();
        let myplaneRect = myplane.getBoundingClientRect();

        if (myplaneRect.left < enemyRect.right &&
            myplaneRect.right > enemyRect.left &&
            myplaneRect.top < enemyRect.bottom &&
            myplaneRect.bottom > enemyRect.top) {
            auto_img.remove();
            myplane.style.backgroundImage = `url(planeb.gif)`;


            // 在一段时间后结束游戏
            setTimeout(function () {
                gameover();
            }, 500);


        }

    }

    requestAnimationFrame(animateBackground);

}

function gameover() {
    // start.style.background = `url("./images/startgame.png") no-repeat center center`
    // start.style.backgroundSize = `cover`
    // //start.style.backgroundImage = `url(./images/startgame.png)`;
    // start.style.display = "block"
    // game.style.display = "none"
    history.go(0);
}

// 开始游戏
begin.onclick = function start_game() {
    //隐藏开始界面
    start.style.background = "none"
    start.style.display = "none"
    game.style.display = "block"
    myplane.style.zIndex = '1';
    //开始动画
    bg1.style.top = "0px"
    bg2.style.top = "-680px"
    animateBackground();

    // 创建一个对象来跟踪哪些键被按下
    let keysDown = {};

    // 监听键盘按键
    window.addEventListener('keydown', function (e) {
        keysDown[e.key] = true;
    });

    window.addEventListener('keyup', function (e) {
        keysDown[e.key] = false;
    });

    // 在requestAnimationFrame的回调函数中更新飞机的位置
    function animatePlane() {
        let newTop, newLeft;

        if (keysDown['ArrowUp']) {
            // 向上移动
            newTop = myplane.offsetTop - myplane_speed;
            if (newTop >= 0) {
                myplane.style.top = newTop + 'px';
            }
        }

        if (keysDown['ArrowDown']) {
            // 向下移动
            newTop = myplane.offsetTop + myplane_speed;
            if (newTop <= game.offsetHeight - myplane.offsetHeight) {
                myplane.style.top = newTop + 'px';
            }
        }

        if (keysDown['ArrowLeft']) {
            // 向左移动
            newLeft = myplane.offsetLeft - myplane_speed;
            if (newLeft >= 0) {
                myplane.style.left = newLeft + 'px';
            }
        }

        if (keysDown['ArrowRight']) {
            // 向右移动
            newLeft = myplane.offsetLeft + myplane_speed;
            if (newLeft <= game.offsetWidth - myplane.offsetWidth) {
                myplane.style.left = newLeft + 'px';
            }
        }

        // 继续动画循环
        requestAnimationFrame(animatePlane);
    }

    // 开始动画
    animatePlane();

    // 监听键盘按键
    window.addEventListener('keydown', function (e) {
        if (e.key === ' ') {
            // 创建一个新的子弹元素
            let bullet = document.createElement('div');
            bullet.className = 'bullet';

            // 设置子弹的背景图片
            bullet.style.backgroundImage = 'url(bullet.png)';
            bullet.style.width = '6px';
            bullet.style.height = '14px';
            bullet.style.backgroundSize = 'cover';
            bullet.style.position = 'absolute';
            bullet.style.zIndex = '1';

            // 添加子弹到游戏区域
            game.appendChild(bullet);

            // 设置子弹的初始位置为飞机的中心
            bullet.style.left = myplane.offsetLeft + myplane.offsetWidth / 2 - bullet.offsetWidth / 2 + 'px';
            bullet.style.top = myplane.offsetTop - bullet.offsetHeight + 'px';

            // 创建一个动画循环来移动子弹
            function animateBullet() {
                // 更新子弹的位置
                bullet.style.top = bullet.offsetTop - bullet_speed + 'px';

                // 检查子弹是否击中了任何敌机
                let enemies = document.querySelectorAll('.enemy');
                // let plane = document.querySelector('.myplane');
                for (let i = 0; i < enemies.length; i++) {
                    let enemy = enemies[i];
                    let enemyRect = enemy.getBoundingClientRect();
                    let bulletRect = bullet.getBoundingClientRect();
                    // let myplaneRect = myplane.getBoundingClientRect();

                    if (bulletRect.left < enemyRect.right &&
                        bulletRect.right > enemyRect.left &&
                        bulletRect.top < enemyRect.bottom &&
                        bulletRect.bottom > enemyRect.top) {
                        // 子弹击中了敌机

                        // 减少敌机的生命值
                        enemy.dataset.health--;

                        // 如果敌机的生命值降到0
                        if (enemy.dataset.health <= 0) {
                            // 替换敌机的背景图片为爆炸图片
                            enemy.style.backgroundImage = `url(${enemy.dataset.boomImage})`;

                            // 在一段时间后删除敌机
                            setTimeout(function () {
                                game.removeChild(enemy);
                            }, 300);
                        }

                        // 删除子弹
                        game.removeChild(bullet);
                        return;
                    }

                    // if (myplaneRect.left < enemyRect.right &&
                    // 	myplaneRect.right > enemyRect.left &&
                    // 	myplaneRect.top < enemyRect.bottom &&
                    // 	myplaneRect.bottom > enemyRect.top) {
                    // 		myplane.style.backgroundImage = `url(./images/planeb.gif)`;

                    // 		gameover();
                    // 	}

                }

                // 如果子弹移动出了游戏区域，那么删除子弹
                if (bullet.offsetTop + bullet.offsetHeight < 0) {
                    game.removeChild(bullet);
                } else {
                    // 否则，继续动画循环
                    requestAnimationFrame(animateBullet);
                }
            }

            // 立即开始动画
            animateBullet();
        }
    });

    // 创建一个函数来生成敌机
    function createEnemy() {
        // 随机选择一个敌机类型
        let random = Math.random();
        let sum = 0;
        let enemyType;
        for (let i = 0; i < enemyTypes.length; i++) {
            sum += enemyTypes[i].probability;
            if (random <= sum) {
                enemyType = enemyTypes[i];
                break;
            }
        }
        // 创建一个新的敌机元素
        let enemy = document.createElement('div');
        enemy.className = 'enemy';

        // 设置敌机的背景图片和大小
        enemy.style.backgroundImage = `url(${enemyType.image})`;
        enemy.style.width = enemyType.width;
        enemy.style.height = enemyType.height;
        enemy.style.backgroundSize = 'cover';
        enemy.style.position = 'absolute'; // 修改这里
        enemy.style.zIndex = '1';

        // 添加敌机到游戏区域
        game.appendChild(enemy);

        // 设置敌机的初始位置
        enemy.style.left = Math.random() * (game.offsetWidth - enemy.offsetWidth) + 'px';
        enemy.style.top = '0px'; // 修改这里

        // 设置敌机的生命值
        enemy.dataset.health = enemyType.health;

        // 存储敌机的boomImage到dataset中
        enemy.dataset.boomImage = enemyType.boomImage;

        // 创建一个动画循环来移动敌机
        function animateEnemy() {
            // 更新敌机的位置
            enemy.style.top = enemy.offsetTop + enemyType.speed + 'px'; // 使用敌机的速度

            // 如果敌机移动出了游戏区域，那么删除敌机
            if (enemy.offsetTop > game.offsetHeight) {
                game.removeChild(enemy);
            } else {
                // 否则，继续动画循环
                requestAnimationFrame(animateEnemy);
            }
        }

        // 立即开始动画
        animateEnemy();
    }

    // 每隔一段时间生成一个新的敌机
    setInterval(createEnemy, 1000); // 你可以根据需要来调整这个值

}