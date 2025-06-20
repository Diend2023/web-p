// 获取主题背景
var body = document.getElementById('body');
// 获取音频播放器对象
var audio = document.getElementById('audioTag');

// 歌曲名
var musicTitle = document.getElementById('music-title');
// 歌曲海报
var recordImg = document.getElementById('record-img');
// 歌曲作者
var author = document.getElementById('author-name');

// 进度条
var progress = document.getElementById('progress');
// 总进度条
var progressTotal = document.getElementById('progress-total');

// 已进行时长
var playedTime = document.getElementById('playedTime');
// 总时长
var audioTime = document.getElementById('audioTime');

// 播放模式按钮
var mode = document.getElementById('playMode');
// 上一首
var skipForward = document.getElementById('skipForward');
// 暂停按钮
var pause = document.getElementById('playPause');
// 下一首
var skipBackward = document.getElementById('skipBackward');
// 音量调节
var volume = document.getElementById('volume');
// 音量调节滑块
var volumeTogger = document.getElementById('volumn-togger');

// 列表
var list = document.getElementById('list');
// 倍速
var speed = document.getElementById('speed');
// MV
var MV = document.getElementById('MV');

// 左侧关闭面板
var closeList = document.getElementById('close-list');
// 音乐列表面板
var musicList = document.getElementById('music-list');

var localMusics = [];
var currentMusicIndex = 0;

// 添加文件输入监听，读取用户选择的本地音频文件，并生成播放列表
var fileInput = document.getElementById('fileInput');
fileInput.addEventListener('change', function (e) {
    localMusics = Array.from(this.files);
    if (localMusics.length > 0) {
        currentMusicIndex = 0;
        updateMusicList();
        loadLocalMusic(currentMusicIndex);
    }
});

// 根据文件列表更新右侧播放队列
function updateMusicList() {
    var listContainer = document.querySelector('.all-list');
    listContainer.innerHTML = "";
    localMusics.forEach(function(file, index) {
        var div = document.createElement('div');
        div.innerText = file.name;
        div.title = file.name;            // 完整文件名悬浮提示
        div.dataset.index = index;
        div.style.cursor = "pointer";
        if (index === currentMusicIndex) {
            div.classList.add('active');
        }
        div.addEventListener('click', function() {
            currentMusicIndex = index;
            initAndPlay();
        });
        listContainer.appendChild(div);
    });
}

// 加载本地音乐文件
function loadLocalMusic(index) {
    if(localMusics.length === 0) return;
    var file = localMusics[index];
    audio.src = URL.createObjectURL(file);
    audio.load();
    // 更新界面显示
    musicTitle.innerText = file.name;
    author.innerText = "未知";
    // 如有需求，可更新唱片/背景图片，此处保持原样
    audio.ondurationchange = function () {
        audioTime.innerText = transTime(audio.duration);
        audio.currentTime = 0;
        updateProgress();
    }
}

// 初始化并播放本地音乐
function initAndPlay() {
    loadLocalMusic(currentMusicIndex);
    pause.classList.remove('icon-play');
    pause.classList.add('icon-pause');
    audio.play();
    rotateRecord();
    updateMusicList(); // 刷新高亮
}

// 暂停/播放功能实现
pause.onclick = function (e) {
    if (audio.paused) {
        audio.play();
        rotateRecord();
        pause.classList.remove('icon-play');
        pause.classList.add('icon-pause');
    } else {
        audio.pause();
        rotateRecordStop();
        pause.classList.remove('icon-pause');
        pause.classList.add('icon-play');
    }
}

// 更新进度条
audio.addEventListener('timeupdate', updateProgress); // 监听音频播放时间并更新进度条
function updateProgress() {
    var value = audio.currentTime / audio.duration;
    progress.style.width = value * 100 + '%';
    playedTime.innerText = transTime(audio.currentTime);
}

//音频播放时间换算
function transTime(value) {
    var time = "";
    var h = parseInt(value / 3600);
    value %= 3600;
    var m = parseInt(value / 60);
    var s = parseInt(value % 60);
    if (h > 0) {
        time = formatTime(h + ":" + m + ":" + s);
    } else {
        time = formatTime(m + ":" + s);
    }

    return time;
}

// 格式化时间显示，补零对齐
function formatTime(value) {
    var time = "";
    var s = value.split(':');
    var i = 0;
    for (; i < s.length - 1; i++) {
        time += s[i].length == 1 ? ("0" + s[i]) : s[i];
        time += ":";
    }
    time += s[i].length == 1 ? ("0" + s[i]) : s[i];

    return time;
}

// 点击进度条跳到指定点播放
progressTotal.addEventListener('mousedown', function (event) {
    // 只有音乐开始播放后才可以调节，已经播放过但暂停了的也可以
    if (!audio.paused || audio.currentTime != 0) {
        var pgsWidth = parseFloat(window.getComputedStyle(progressTotal, null).width.replace('px', ''));
        var rate = event.offsetX / pgsWidth;
        audio.currentTime = audio.duration * rate;
        updateProgress(audio);
    }
});

// 点击列表展开音乐列表
list.addEventListener('click', function (event) {
    musicList.classList.remove("list-card-hide");
    musicList.classList.add("list-card-show");
    musicList.style.display = "flex";
    closeList.style.display = "flex";
    closeList.addEventListener('click', closeListBoard);
});

// 点击关闭面板关闭音乐列表
function closeListBoard() {
    musicList.classList.remove("list-card-show");
    musicList.classList.add("list-card-hide");
    closeList.style.display = "none";
}

// // 存储当前播放的音乐序号
// var musicId = 0;

// // 后台音乐列表
// let musicData = [['洛春赋', '云汐'], ['Yesterday', 'Alok/Sofi Tukker'], ['江南烟雨色', '杨树人'], ['Vision pt.II', 'Vicetone']];

// 播放模式设置
var modeId = 1;
mode.addEventListener('click', function () {
    modeId = modeId % 3 + 1;
    mode.style.backgroundImage = "url('mode" + modeId + ".png')";
});

audio.onended = function () {
    if (localMusics.length === 0) return;
    if (modeId === 2) {
        currentMusicIndex = (currentMusicIndex + 1) % localMusics.length;
    } else if (modeId === 3) {
        var old = currentMusicIndex;
        do {
            currentMusicIndex = Math.floor(Math.random() * localMusics.length);
        } while (currentMusicIndex === old);
    }
    initAndPlay();
};

skipForward.onclick = function () {
    if (localMusics.length === 0) return;
    currentMusicIndex = (currentMusicIndex - 1 + localMusics.length) % localMusics.length;
    initAndPlay();
};

skipBackward.onclick = function () {
    if (localMusics.length === 0) return;
    currentMusicIndex = (currentMusicIndex + 1) % localMusics.length;
    initAndPlay();
};

// 刷新唱片旋转角度
function refreshRotate() {
    recordImg.classList.add('rotate-play');
}

// 使唱片旋转
function rotateRecord() {
    recordImg.style.animationPlayState = "running"
}

// 停止唱片旋转
function rotateRecordStop() {
    recordImg.style.animationPlayState = "paused"
}

// 存储上一次的音量
var lastVolumn = 70

// 滑块调节音量
audio.addEventListener('timeupdate', updateVolumn);
function updateVolumn() {
    audio.volume = volumeTogger.value / 70;
}

// 点击音量调节设置静音
volume.addEventListener('click', setNoVolumn);
function setNoVolumn() {
    if (volumeTogger.value == 0) {
        if (lastVolumn == 0) {
            lastVolumn = 70;
        }
        volumeTogger.value = lastVolumn;
        volume.style.backgroundImage = "url('音量.png')";
    }
    else {
        lastVolumn = volumeTogger.value;
        volumeTogger.value = 0;
        volume.style.backgroundImage = "url('静音.png')";
    }
}
