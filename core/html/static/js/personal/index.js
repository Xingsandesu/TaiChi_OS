let cpuChart, memoryChart;

const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
const socket = new WebSocket(`${protocol}//${window.location.hostname}/Monitor`);
let recvData = null;
socket.onmessage = function (event) {
    recvData = JSON.parse(event.data);
    handleResponse(recvData, cpuChart, memoryChart);
};

function checkUserAgent() {
    var isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
    if (isMobile) {
        var metaTag = document.createElement('meta');
        metaTag.name = "viewport";
        metaTag.content = "width=500";
        document.getElementsByTagName('head')[0].appendChild(metaTag);
    }
}

checkUserAgent();

function createChart(ctx, gradient, title) {
    return new Chart(ctx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [0, 100],
                backgroundColor: [gradient, '#ddd']
            }]
        },
        options: {
            title: {
                display: true,
                text: title
            },
            animation: {
                animateScale: true,
                animateRotate: true,
                duration: 2000
            }
        }
    });
}

function getSystemInfo(diskChart) {
    fetch('/api/info')
        .then(response => response.json())
        .then(response => {
            if (response.code === 200) {
                const data = response.data;
                document.getElementById('systemVersion').innerText = data.system_version;
                document.getElementById('diskUsageLabel').querySelector('.usage').textContent = data.disk_usage + '%';
                diskChart.data.datasets[0].data = [data.disk_usage, 100 - data.disk_usage];
                diskChart.update({
                    duration: 2000,
                    easing: 'easeOutBounce'
                });
            } else {
                console.error(response.errmsg);
            }
        });
}

function handleResponse(data, cpuChart, memoryChart) {
    if (!cpuChart || !memoryChart) {
        console.error('cpuChart or memoryChart is not defined');
        return;
    }
    cpuChart.data.datasets[0].data = [data.cpu.load1[data.cpu.load1.length - 1], 100 - data.cpu.load1[data.cpu.load1.length - 1]];
    memoryChart.data.datasets[0].data = [data.ram.memory[data.ram.memory.length - 1], 100 - data.ram.memory[data.ram.memory.length - 1]];
    cpuChart.update({
        duration: 2000,
        easing: 'easeOutBounce'
    });
    memoryChart.update({
        duration: 2000,
        easing: 'easeOutBounce'
    });
    document.getElementById('cpuUsageLabel').querySelector('.usage').textContent = data.cpu.load1[data.cpu.load1.length - 1] + '%';
    document.getElementById('memoryUsageLabel').querySelector('.usage').textContent = data.ram.memory[data.ram.memory.length - 1] + '%';
    document.getElementById('uploadLabel').textContent = '上传: ' + formatBytes(data.network.upload[data.network.upload.length - 1]) + '/s';
    document.getElementById('downloadLabel').textContent = '下载: ' + formatBytes(data.network.download[data.network.download.length - 1]) + '/s';
}

function formatBytes(bytes) {
    const units = ['KB', 'MB', 'GB'];
    let i;
    bytes /= 1024;
    for (i = 0; bytes >= 1024 && i < units.length - 1; i++) {
        bytes /= 1024;
    }
    return bytes.toFixed(2) + ' ' + units[i];
}

document.addEventListener('DOMContentLoaded', function () {
    const cpuCtx = document.getElementById('cpuUsageChart').getContext('2d');
    const memoryCtx = document.getElementById('memoryUsageChart').getContext('2d');
    const diskCtx = document.getElementById('diskUsageChart').getContext('2d');
    const cpuGradient = cpuCtx.createLinearGradient(0, 0, 0, 400);
    cpuGradient.addColorStop(0, 'rgba(255, 99, 132, 0.5)');
    cpuGradient.addColorStop(1, 'rgba(255, 99, 132, 0.2)');
    const memoryGradient = memoryCtx.createLinearGradient(0, 0, 0, 400);
    memoryGradient.addColorStop(0, 'rgba(54, 162, 235, 0.5)');
    memoryGradient.addColorStop(1, 'rgba(54, 162, 235, 0.2)');
    const diskGradient = diskCtx.createLinearGradient(0, 0, 0, 400);
    diskGradient.addColorStop(0, 'rgba(75, 192, 192, 0.5)');
    diskGradient.addColorStop(1, 'rgba(75, 192, 192, 0.2)');
    cpuChart = createChart(cpuCtx, cpuGradient, 'CPU 使用率');
    memoryChart = createChart(memoryCtx, memoryGradient, '内存 使用率');
    const diskChart = createChart(diskCtx, diskGradient, '磁盘 使用率');
    getSystemInfo(diskChart);

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.hostname}/Monitor`);
    let recvData = null;
    socket.onmessage = function (event) {
        recvData = JSON.parse(event.data);
        handleResponse(recvData, cpuChart, memoryChart);
    };
    $(window).resize(function () {
        if (cpuChart) {
            cpuChart.resize();
            cpuChart.update();
        }
        if (memoryChart) {
            memoryChart.resize();
            memoryChart.update();
        }
        if (diskChart) {
            diskChart.resize();
            diskChart.update();
        }
    });
}, 1000);

window.onload = function () {
    const blocks = document.getElementsByClassName('usage-block');  // 修改这里
    const systemVersion = document.getElementById('systemVersion');

    for (let i = 0; i < blocks.length; i++) {
        blocks[i].style.opacity = "1";
    }

    setTimeout(function () {
        systemVersion.style.opacity = "1";
    });
}

$(document).ready(function () {
    let cpuEcho = null;
    let ramEcho = null;
    let networkEcho = null;
    let diskIOEcho = null;

    const cpuDisplay = function (time, x, y, z) {
        const cpuChart = document.getElementById("CPUchart");
        if (cpuChart) {
            setTimeout(function () {
                if (cpuEcho === null) {
                    cpuEcho = echarts.init(cpuChart);
                }
                const option = {
                    title: {
                        left: 'left',
                        text: 'CPU 实时利用率',
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        }
                    },
                    //legend: {
                    //    left: 'right',  // 设置图例的位置为右侧
                    //    data: ['1分钟负载', '5分钟负载', '15分钟负载']
                    //},
                    xAxis: {
                        type: 'category',
                        data: time
                    },
                    yAxis: {
                        type: 'value',
                        axisLabel: {
                            formatter: '{value} %'  // 添加百分号
                        }
                    },
                    series: [
                        {
                            name: "1分钟负载",
                            stack: "总量",
                            data: x,
                            type: 'line',
                            smooth: true,  // 添加此行以使线条平滑
                            areaStyle: {}
                        },
                        {
                            name: "5分钟负载",
                            stack: "总量",
                            data: y,
                            type: 'line',
                            smooth: true,  // 添加此行以使线条平滑
                            areaStyle: {}
                        },
                        {
                            name: "15分钟负载",
                            stack: "总量",
                            data: z,
                            type: 'line',
                            smooth: true,  // 添加此行以使线条平滑
                            areaStyle: {}
                        }
                    ]
                };
                cpuEcho.setOption(option, true);
            }, 0);
        }
    };

    const ramDisplay = function (time, x) {
        const ramChart = document.getElementById("RAMchart");
        if (ramChart) {
            setTimeout(function () {
                if (ramEcho === null) {
                    ramEcho = echarts.init(ramChart);
                }
                const option = {
                    title: {
                        left: 'left',
                        text: '内存实时利用率',
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        }
                    },
                    //legend: {
                    //    left: 'right',  // 设置图例的位置为右侧
                    //    data: ['内存使用率']
                    //},
                    xAxis: {
                        type: 'category',
                        data: time
                    },
                    yAxis: {
                        type: 'value',
                        axisLabel: {
                            formatter: '{value} %'  // 添加百分号
                        }
                    },
                    series: [{
                        name: "内存使用率",
                        stack: "总量",
                        data: x,
                        type: 'line',
                        smooth: true,  // 添加此行以使线条平滑
                        areaStyle: {}
                    }]
                };
                ramEcho.setOption(option, true);
            }, 0);
        }
    };

    const networkDisplay = function (time, upload, download) {
        // 自动转换单位的函数
        const formatBytes = function (bytes) {
            const units = ['B', 'KB', 'MB', 'GB'];
            let unit = 'B';
            for (let i = 0; i < units.length; i++) {
                if (bytes < 1024) {
                    unit = units[i];
                    break;
                }
                bytes /= 1024;
            }
            return Math.round(bytes) + ' ' + unit;
        };

        const networkChart = document.getElementById("NETWORKchart");
        if (networkChart) {
            setTimeout(function () {
                if (networkEcho === null) {
                    networkEcho = echarts.init(networkChart);
                }
                const option = {
                    title: {
                        left: 'left',
                        text: '网络流量动态',
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        },
                        formatter: function (params) {
                            return params[0].name + '<br/>' +
                                params[0].seriesName + ': ' + formatBytes(params[0].value) + '<br/>' +
                                params[1].seriesName + ': ' + formatBytes(params[1].value);
                        }
                    },
                    //legend: {
                    //left: 'right',  // 设置图例的位置为右侧
                    //data: ['上传速度', '下载速度']
                    //},
                    xAxis: {
                        type: 'category',
                        data: time
                    },
                    yAxis: {
                        type: 'value',
                        axisLabel: {
                            formatter: function (value) {
                                return formatBytes(value);
                            }
                        }
                    },
                    series: [
                        {
                            name: "上传速度",
                            data: upload,
                            type: 'line',
                            smooth: true,
                            areaStyle: {}
                        },
                        {
                            name: "下载速度",
                            data: download,
                            type: 'line',
                            smooth: true,
                            areaStyle: {}
                        }
                    ]
                };
                networkEcho.setOption(option, true);
            }, 0);
        }
    };

    const diskIODisplay = function (time, disk_read, disk_write) {
        // 自动转换单位的函数
        const formatBytes = function (bytes) {
            const units = ['B', 'KB', 'MB', 'GB'];
            let unit = 'B';
            for (let i = 0; i < units.length; i++) {
                if (bytes < 1024) {
                    unit = units[i];
                    break;
                }
                bytes /= 1024;
            }
            return Math.round(bytes) + ' ' + unit;
        };
        const diskIOChart = document.getElementById("DiskIOChart");
        if (diskIOChart) {
            setTimeout(function () {
                if (diskIOEcho === null) {
                    diskIOEcho = echarts.init(diskIOChart);
                }
                const option = {
                    title: {
                        left: 'left',
                        text: 'I/O动态',
                    },
                    grid: {
                        left: '3%',
                        right: '4%',
                        bottom: '3%',
                        containLabel: true
                    },
                    tooltip: {
                        trigger: 'axis',
                        axisPointer: {
                            type: 'cross',
                            label: {
                                backgroundColor: '#6a7985'
                            }
                        },
                        formatter: function (params) {
                            return params[0].name + '<br/>' +
                                params[0].seriesName + ': ' + formatBytes(params[0].value) + '<br/>' +
                                params[1].seriesName + ': ' + formatBytes(params[1].value);
                        }
                    },
                    //legend: {
                    //    left: 'right',  // 设置图例的位置为右侧
                    //    data: ['读取速度', '写入速度']
                    //},
                    xAxis: {
                        type: 'category',
                        data: time
                    },
                    yAxis: {
                        type: 'value',
                        axisLabel: {
                            formatter: function (value) {
                                return formatBytes(value);
                            }
                        }
                    },
                    series: [
                        {
                            name: "读取速度",
                            data: disk_read,
                            type: 'line',
                            smooth: true,
                            areaStyle: {}
                        },
                        {
                            name: "写入速度",
                            data: disk_write,
                            type: 'line',
                            smooth: true,
                            areaStyle: {}
                        }
                    ]
                };
                diskIOEcho.setOption(option, true);
            }, 0);
        }
    };
    // 添加 resize 事件的监听器
    $(window).resize(function () {
        if (cpuEcho) {
            cpuEcho.resize();
        }
        if (ramEcho) {
            ramEcho.resize();
        }
        if (networkEcho) {
            networkEcho.resize();
        }
        if (diskIOEcho) {
            diskIOEcho.resize();
        }
    });


    setInterval(function () {
        if (recvData !== null) {
            cpuDisplay(recvData.datetime, recvData.cpu.load1, recvData.cpu.load5, recvData.cpu.load15);
            ramDisplay(recvData.datetime, recvData.ram.memory);
            networkDisplay(recvData.datetime, recvData.network.upload, recvData.network.download);
            diskIODisplay(recvData.datetime, recvData.diskIO.disk_read, recvData.diskIO.disk_write);
            recvData = null;
        }
    }, 1000);
});

// 获取日期和时间
function updateTime() {
    let now = new Date();
    let dateOptions = {weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'};
    let date = now.toLocaleDateString('zh-CN', dateOptions);
    let timeOptions = {hour: '2-digit', minute: '2-digit'};
    let time = now.toLocaleTimeString([], timeOptions);
    document.getElementById('dateLabel').innerText = date;
    document.getElementById('timeLabel').innerText = time;
}

// 更新日期、时间
updateTime();
// 每秒更新一次时间
setInterval(updateTime, 1000);

var refreshIntervalId;

$(document).ready(function () {
    function refresh() {
        loadContainers();
        $("#outer").load(location.href + " #outer>*", "");
        setTimeout(refresh, 10000);  // 每10秒刷新一次
    }
    refresh();
});

function loadContainers() {
    $.get("/api/containers", function (data) {
        if (data.code === 200) {
            var rows = "";
            data.data.forEach(function (container) {
                var name = container.Name.substring(1);  // 去掉名称前面的"/"
                var row = "<tr>";
                row += "<td>" + name + "</td>";
                row += "<td>" + container.Config.Image + "</td>";
                var portMappings = formatPortMappings(container);  // 更改了这里
                row += "<td>" + portMappings.hostPort + "</td>";
                row += "<td>" + container.State.Status + "</td>";
                if (container.State.Status === "running") {
                    row += "<td>";
                    row += "<div class='btn-grid'>";
                    row += "<button class='btn btn-custom btn-sm m-1' onclick='stopContainer(\"" + name + "\")'>停止</button>";
                    row += "<button class='btn btn-custom btn-sm m-1' onclick='stopAndDeleteContainer(\"" + name + "\")'>停止并删除</button>";
                    row += "</div>";
                    row += "</td>";
                } else {
                    row += "<td>";
                    row += "<div class='btn-grid'>";
                    row += "<button class='btn btn-custom btn-sm m-1' onclick='startContainer(\"" + name + "\")'>启动</button>";
                    row += "<button class='btn btn-custom btn-sm m-1' onclick='deleteContainer(\"" + name + "\")'>删除</button>";
                    row += "</div>";
                    row += "</td>";
                }
                rows += row;
            });
            $("#containersTable tbody").html(rows);
        }
    });
}


function formatPortMappings(container) {
    if (container.HostConfig && container.HostConfig.NetworkMode === "host") {
        return {containerPort: "Host网络", hostPort: "Host网络"};
    } else if (container.HostConfig.NetworkMode.startsWith("macvlan")) {
        return {containerPort: "Macvlan网络", hostPort: "Macvlan网络"};
    } else if (!container.HostConfig.PortBindings || Object.keys(container.HostConfig.PortBindings).length === 0) {
        return {containerPort: "无映射", hostPort: "无映射"};
    }
    var result = {containerPort: "", hostPort: ""};
    for (var key in container.HostConfig.PortBindings) {
        var containerPort = key;
        var hostPort = container.HostConfig.PortBindings[key][0].HostPort;
        result.containerPort += containerPort;
        result.hostPort += hostPort;
    }
    return result;
}


function stopContainer(name) {
    clearInterval(refreshIntervalId);  // 停止自动刷新
    var button = $("button[onclick='stopContainer(\"" + name + "\")']");
    button.text('停止中...');  // 更改按钮文本

    $.post("/api/containers/" + name + "/stop", function (data) {
        if (data.code === 200) {
            loadContainers();
            $("#outer").load(location.href + " #outer>*", "");
        }
        button.text('停止');  // 将按钮文本更改回来
        refreshIntervalId = setInterval(loadContainers, 5000);  // 重新开始自动刷新
    });
}

function deleteContainer(name) {
    clearInterval(refreshIntervalId);  // 停止自动刷新
    var button = $("button[onclick='deleteContainer(\"" + name + "\")']");
    button.text('删除中...');  // 更改按钮文本

    $.ajax({
        url: "/api/containers/" + name + "/delete",
        type: 'DELETE',
        success: function (data) {
            if (data.code === 200) {
                loadContainers();
                $("#outer").load(location.href + " #outer>*", "");
            }
            button.text('删除');  // 将按钮文本更改回来
            refreshIntervalId = setInterval(loadContainers, 5000);  // 重新开始自动刷新
        }
    });
}


function startContainer(name) {
    clearInterval(refreshIntervalId);
    var button = $("button[onclick='startContainer(\"" + name + "\")']");
    button.text('启动中...');

    $.post("/api/containers/" + name + "/start", function (data) {
        if (data.code === 200) {
            loadContainers();
            $("#outer").load(location.href + " #outer>*", "");
        }
        button.text('启动');
        refreshIntervalId = setInterval(loadContainers, 5000);
    });
}

function stopAndDeleteContainer(name) {
    clearInterval(refreshIntervalId);
    var button = $("button[onclick='stopAndDeleteContainer(\"" + name + "\")']");
    button.text('进行中...');

    $.ajax({
        url: "/api/containers/" + name + "/stop_and_delete",
        type: 'DELETE',
        success: function (data) {
            if (data.code === 200) {
                loadContainers();
                $("#outer").load(location.href + " #outer>*", "");
            }
            button.text('停止并删除');
            refreshIntervalId = setInterval(loadContainers, 5000);
        }
    });
}
