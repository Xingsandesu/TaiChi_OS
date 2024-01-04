/*
函数定义
*/

//创建一个目录项 full_path为目录绝对路径, name为目录名字
function create_item(full_path, name) {
    //创建一个button来存放一个子目录
    var $list_item = $(document.createElement('button'));
    $list_item.addClass('list-group-item');
    $list_item.data('status', 'unload');  //设置状态为未加载

    //存储该子目录绝对路径
    $list_item.data('dst', full_path);

    //添加图标
    $list_item.append('<span class="bi bi-folder-fill"></span>');

    //创建显示子目录名的span标签
    var $path = $(document.createElement('span'));
    $path.addClass('path');
    $path.text(name);  //设置显示的目录名
    $list_item.append($path);  //添加该span标签到button中

    //设置事件
    $list_item.click(function () {
        var $t = $(this);
        return click_dir($t);
    });

    return $list_item;  //返回创建好的元素
}

//加载dst目录下的子目录到$t元素中
function load_dir($t, dst) {

    $.post('/api/listdir/', {dir: dst}, function (response) {
        if (response['code'] == 200) {
            var dirs = response['data']['dirs'];
            //console.log(dirs);  //debug

            //创建一个容器作为列表来放置所有子目录
            var $list_group = $(document.createElement('div'));
            $list_group.addClass('list-group');  //为容器添加类

            //为所有子目录创建列表项
            for (var i = 0; i < dirs.length; i++) {
                var dir = dirs[i];  //该子目录名
                var full_path = dst + '/' + dir;  //该子目录的绝对路径

                //创建列表项
                var $list_item = create_item(full_path, dir)

                //添加子目录到列表中
                $list_group.append($list_item);
            }

            //添加子目录列表到自身中
            $t.append($list_group);
        } else {
            alert(response['errmsg']);
        }
    }, 'json');

}

//复制/移动 浏览窗口中的路径被点击调用的函数
function click_dir($t) {
    var dst = $t.data('dst');  //自身代表的目录
    var operation = $('#save_data').data('operation');  //操作
    var text = operation + '到' + dst;
    $('#dst_selected').text(text);  //设置对话框标题显示当前操作

    //存储本目录作为 复制/移动 的目标目录
    $('#save_data').data('dst', dst);

    //获取目录的状态
    var status = $t.data('status');

    if (status == 'unload') {  //如果当前目录状态是未加载就加载数据

        //加载本目录下的所有子目录名;
        load_dir($t, dst);

        $t.data('status', 'open');  //设置状态为打开

    } else if (status == 'open') {  //如果当前状态是打开就关闭目录
        $t.children('.list-group').first().hide();
        $t.data('status', 'close');  //设置状态为关闭
    } else {  //当前状态是关闭就打开
        $t.children('.list-group').first().show();
        $t.data('status', 'open');  //设置状态为打开
    }

    return false;  //防止冒泡
}

//加载完后设定一些事件
window.onload = function () {

    //监听.only-input弹出层弹出显示完全 聚焦到input控件上
    $('.only-input').each(function () {
        var $t = $(this);
        $t.on('shown.bs.modal', function () {
            $t.find('input').first().focus();  //让输入框获取焦点
        });
    });

    //监听目录名输入框的回车键按下
    $('#dir_name_input').keydown(function (e) {
        if (e.keyCode == 13) {
            $('#new_dir_btn').click();  //点击确认按钮
        }
    });

    //新建目录确认键按下, 创建目录
    $('#new_dir_btn').click(function () {
        var dir = $('#save_data').data('path');
        var name = $('#dir_name_input').val();

        $.post('/api/mkdir/', {dir: dir, name: name}, function (response) {
            if (response['code'] == 200) {
                window.location.reload(); //刷新页面
            } else {
                alert(response['errmsg']);
            }
        }, 'json');
    });

    //文件上传确认按钮被按下
    $('#upload_btn').click(function () {
        var path = $('#save_data').data('path');  //本页面的路径
        var files = $('#file_input')[0].files;
        if (files.length > 0) {
            var form_data = new FormData();
            form_data.append('dir', path);

            for (var i = 0; i < files.length; i++) {
                form_data.append('files', files[i]);
            }

            $.ajax({
                url: '/api/upload/',
                type: 'post',
                cache: false,
                data: form_data,
                contentType: false,
                processData: false,
                datatype: 'JSON',
                success: function (response) {
                    if (response['code'] == 200) {
                        window.location.reload();
                    } else {
                        alert(response['errmsg']);
                    }
                },
                error: function () {
                    alert('操作失败.');
                }
            });

        }
    });

    //重命名按钮被按下
    $('.btn-rename').each(function (index) {
        var $t = $(this);
        $t.click(function () {
            var li = $('.btn-group-li')[index];  //获取存储了该文件或目录的路径的元素
            var src = $(li).data('path');  //获取源路径
            var $save_data = $('#save_data');  //获取#save_data元素来存取数据


            $save_data.data('rename_path', src);  //存储源文件路径

            $('#rename_modal').modal('show');  //显示弹出层

            return false;  //防止冒泡
        });
    });

    //监听 新文件/目录名 输入框的回车键按下
    $('#rename_input').keydown(function (e) {
        if (e.keyCode == 13) {
            $('#rename_btn').click();  //点击确认按钮
        }
    });

    //重命名 文件/目录 确认按钮被按下
    $('#rename_btn').click(function () {
        var path = $('#save_data').data('rename_path');  // 文件/目录 的路径
        var name = $('#rename_input').val();  //新的名字

        $.post('/api/rename/', {path: path, name: name}, function (response) {
            if (response['code'] == 200) {
                window.location.reload();
            } else {
                alert(response['errmsg']);
            }
        });

    });

    //移动按钮被按下
    $('.btn-move').each(function (index) {
        var $t = $(this);
        $t.click(function () {
            var li = $('.btn-group-li')[index];  //获取存储了该文件或目录的路径的元素
            var src = $(li).data('path');  //获取源路径
            $('#save_data').data('src', src);  //存储源路径
            $('#save_data').removeData('src').data('src', src);  //移除旧的源路径并存储新的源路径
            $('#save_data').data('operation', '移动');

            $('#cp_mv_modal').modal('show');  //显示弹出层

            return false;  //防止冒泡
        });
    });

    //复制按钮被按下
    $('.btn-copy').each(function (index) {
        var $t = $(this);
        $t.click(function () {
            var li = $('.btn-group-li')[index];  //获取存储了该文件或目录的路径的元素
            var src = $(li).data('path');  //获取源路径
            $('#save_data').data('src', src);  //存储源路径
            $('#save_data').removeData('src').data('src', src);  //移除旧的源路径并存储新的源路径
            $('#save_data').data('operation', '复制');

            $('#cp_mv_modal').modal('show');  //显示弹出层

            return false;  //防止冒泡
        });
    });

    //删除按钮被按下
    $('.btn-remove').each(function (index) {
        var $t = $(this);
        var path = $($('.btn-group-li')[index]).data('path');
        //console.log(path);
        $t.click(function () {
            if (confirm('确认删除?')) {
                $.post('/api/remove/', {path: path}, function (response) {
                    if (response['code'] == 200) {
                        window.location.reload(); //重新加载页面
                    } else {
                        alert(response['errmsg']);
                    }
                }, 'json');
            }

            return false; //防止冒泡
        });
    });

    //选择 复制/移动 的位置后按下确认键
    $('#cp_mv_btn').click(function () {
        var src = $('#save_data').data('src');  //获取源路径
        var dst = $('#save_data').data('dst'); //获取目标路径
        var operation = $('#save_data').data('operation');  //获取操作方法

        var url = '';
        if (operation == 'copy') {
            url = '/api/copy/';
        } else if (operation == 'move') {
            url = '/api/move/';
        }

        if (url) {
            $.post(url, {src: src, dst: dst}, function (response) {
                if (response['code'] == 200) {
                    window.location.reload(); //刷新页面
                } else {
                    alert(response['errmsg']);
                }
            });
        } else {
            alert('操作失败!');
        }

    });

    //复制/移动 窗口中的路径被点击
    $('#cp_mv_modal .modal-body button').each(function () {
        var $t = $(this);
        $t.click(function () {
            return click_dir($t);
        });
    });

};

// 初始化CodeMirror编辑器
var editor = CodeMirror(document.getElementById("editor"), {
    lineNumbers: true,
    theme: "monokai",
    mode: "javascript"
});

// 为查看文件按钮添加点击事件
$('.btn-view').click(function () {
    var path = $(this).data('path');

    // 调用获取文件内容的API
    $.get('/api/view/', {path: path}, function (data) {
        if (data.code === 200 && data.data && data.data.editable) {  // 检查data.data是否存在
            // 将返回的内容显示在CodeMirror编辑器中
            editor.setValue(data.data.content);
            // 设置#save_data元素的data-path属性
            $('#save_data').data('path', path);
            // 打开模态窗口
            $('#view_file_modal').modal('show');
        } else {
            // 如果code字段的值等于CODE_NO，显示errmsg字段的值
            alert(data.errmsg || '发生了错误');
        }
    });

    // 当模态窗口完全打开后，重新计算CodeMirror编辑器的尺寸
    $('#view_file_modal').on('shown.bs.modal', function () {
        editor.refresh();
    });

    // 为保存按钮添加点击事件
    $('#save_btn').click(function () {
        var path = $('#save_data').data('path');
        var codeMirrorContent = editor.getValue();

        // 调用保存文件内容的API
        $.post('/api/edit/', {path: path, content: codeMirrorContent}, function (data) {
            if (data.code === 200) {
                alert('保存成功');
                // 关闭模态窗口
                $('#view_file_modal').modal('hide');
            } else {
                alert(data.errmsg);
            }
        });
    });
});