const term = new Terminal();
term.open(document.getElementById('terminal'));
const fitAddon = new FitAddon.FitAddon();
term.loadAddon(fitAddon);
fitAddon.fit();

function runCommand(command) {
    term.clear();  // 清除终端内容
    $.ajax({
        url: '/api/command',
        type: 'post',
        contentType: 'application/json',
        data: JSON.stringify({command: command}),
        success: function (response) {
            if (response.code === 200) {
                term.writeln(response.data.output);
                if (response.data.error) {
                    term.writeln(response.data.error);
                }
            } else {
                term.writeln(response.errmsg);
            }
        }
    });
}

$('.run_command').click(function () {
    const command = $(this).data('command');
    runCommand(command);
});