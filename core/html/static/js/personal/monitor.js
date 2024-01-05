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
                    legend: {
                        left: 'right',  // 设置图例的位置为右侧
                        data: ['1分钟负载', '5分钟负载', '15分钟负载']
                    },
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
                    legend: {
                        left: 'right',  // 设置图例的位置为右侧
                        data: ['内存使用率']
                    },
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
            return bytes.toFixed(2) + ' ' + unit;
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
                    legend: {
                        left: 'right',  // 设置图例的位置为右侧
                        data: ['上传速度', '下载速度']
                    },
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
            return bytes.toFixed(2) + ' ' + unit;
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
                    legend: {
                        left: 'right',  // 设置图例的位置为右侧
                        data: ['读取速度', '写入速度']
                    },
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

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(`${protocol}//${window.location.hostname}/Monitor`);
    let recvData = null;
    socket.onmessage = function (event) {
        recvData = JSON.parse(event.data);
    };

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
