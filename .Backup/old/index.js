const socket = io('/Monitor');
// 当文档加载完成后执行函数
document.addEventListener('DOMContentLoaded', function() {
    // 获取三个图表的绘图上下文
    const cpuCtx = document.getElementById('cpuUsageChart').getContext('2d');
    const memoryCtx = document.getElementById('memoryUsageChart').getContext('2d');
    const diskCtx = document.getElementById('diskUsageChart').getContext('2d');

    // 创建三个渐变色，用于填充图表
    const cpuGradient = cpuCtx.createLinearGradient(0, 0, 0, 400);
    cpuGradient.addColorStop(0, 'rgba(255, 99, 132, 0.5)');
    cpuGradient.addColorStop(1, 'rgba(255, 99, 132, 0.2)');

    const memoryGradient = memoryCtx.createLinearGradient(0, 0, 0, 400);
    memoryGradient.addColorStop(0, 'rgba(54, 162, 235, 0.5)');
    memoryGradient.addColorStop(1, 'rgba(54, 162, 235, 0.2)');

    const diskGradient = diskCtx.createLinearGradient(0, 0, 0, 400);
    diskGradient.addColorStop(0, 'rgba(75, 192, 192, 0.5)');
    diskGradient.addColorStop(1, 'rgba(75, 192, 192, 0.2)');

    // 创建三个环形图表，显示CPU、内存和磁盘的使用情况
    const cpuChart = new Chart(cpuCtx, {
        type: 'doughnut',
        data: {
            //labels: ['已使用', '未使用'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [cpuGradient, '#ddd']
            }]
        },
        options: {
            title: {
                display: true,
                text: 'CPU 使用率'
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2000  // 动画持续时间为2秒
            }
        }
    });

    const memoryChart = new Chart(memoryCtx, {
        type: 'doughnut',
        data: {
            //labels: ['已使用', '未使用'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [memoryGradient, '#ddd']
            }]
        },
        options: {
            title: {
                display: true,
                text: '内存 使用率'
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2000  // 动画持续时间为2秒
            }
        }
    });

    const diskChart = new Chart(diskCtx, {
        type: 'doughnut',
        data: {
            //labels: ['已使用', '未使用'],
            datasets: [{
                data: [0, 100],
                backgroundColor: [diskGradient, '#ddd']
            }]
        },
        options: {
            title: {
                display: true,
                text: '磁盘 使用率'
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2000  // 动画持续时间为2秒
            }
        }
    });

    // 在页面加载完成后，从服务器获取一次系统版本信息和磁盘使用情况
    fetch('/api/info')
    .then(response => response.json())
    .then(data => {
        // 更新系统版本显示
        document.getElementById('systemVersion').innerText = data.system_version;
    
        // 更新磁盘使用率显示
        document.getElementById('diskUsageLabel').querySelector('.usage').textContent = data.disk_usage + '%';
    
        // 更新磁盘使用率图表
        diskChart.data.datasets[0].data = [data.disk_usage, 100 - data.disk_usage];
        diskChart.update({
            duration: 2000,
            easing: 'easeOutBounce'
        });
    });

    // 从WebSocket接收数据，并更新图表
    socket.on('response', function(data) {
        // 更新图表的数据
        cpuChart.data.datasets[0].data = [data.cpu.load1[data.cpu.load1.length - 1], 100 - data.cpu.load1[data.cpu.load1.length - 1]];
        memoryChart.data.datasets[0].data = [data.ram.memory[data.ram.memory.length - 1], 100 - data.ram.memory[data.ram.memory.length - 1]];

        // 在数据更新之后调用update方法
        cpuChart.update({
            duration: 2000,
            easing: 'easeOutBounce'
        });
        memoryChart.update({
            duration: 2000,
            easing: 'easeOutBounce'
        });

        // 更新同心圆中的占用率显示
        document.getElementById('cpuUsageLabel').querySelector('.usage').textContent = data.cpu.load1[data.cpu.load1.length - 1] + '%';
        document.getElementById('memoryUsageLabel').querySelector('.usage').textContent = data.ram.memory[data.ram.memory.length - 1] + '%';

        // 更新网络上传下载速度显示
        document.getElementById('uploadLabel').textContent = '上传: ' + formatBytes(data.network.upload[data.network.upload.length - 1]) + '/s';
        document.getElementById('downloadLabel').textContent = '下载: ' + formatBytes(data.network.download[data.network.download.length - 1]) + '/s';
    });

        // 将字节数格式化为易读的字符串
        function formatBytes(bytes) {
            const units = ['KB', 'MB', 'GB'];
            let i;
            bytes /= 1024;  // 将字节转换为KB
            for (i = 0; bytes >= 1024 && i < units.length - 1; i++) {
                bytes /= 1024;
            }
            return bytes.toFixed(2) + ' ' + units[i];
        }
    }, 1000);




// 使得页面加载完成后，获取的属性的动画效果(透明度为1, 之前为0, 为了实现淡入效果,@主页仪表动画效果)
window.onload = function() {
    const blocks = document.getElementsByClassName('item-block');
    const systemVersion = document.getElementById('systemVersion');

    for (let i = 0; i < blocks.length; i++) {
        blocks[i].style.opacity = "1";
    }

    // 将systemVersion元素的透明度设置为1，使其淡入
    setTimeout(function() {
        systemVersion.style.opacity = "1";
    }, 1000); // 1秒后执行
}