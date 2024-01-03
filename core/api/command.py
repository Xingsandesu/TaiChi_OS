# import subprocess
#
# import chardet
# from flask import request
# from flask_login import login_required
# from core.config import CODE_YES, CODE_NO
# from .blueprint import bp
# from .josnify import create_api_response
#
#
# @bp.route('/command', methods=['POST'])
# @login_required
# def run_command():
#     # 验证输入
#     if not request.json or 'command' not in request.json or not isinstance(request.json['command'], str):
#         # 如果请求不是 JSON 格式，或者 'command' 不在请求数据中，或者 'command' 不是字符串类型，返回错误信息
#         return create_api_response(CODE_NO, 'Invalid input')
#
#     command = request.json['command']  # 从请求数据中获取 'command'
#
#     try:
#         # 使用 subprocess.run 运行命令，shell=True 表示命令将在 shell 中执行，check=True 表示如果命令返回非零退出状态，将引发 CalledProcessError
#         # stdout=subprocess.PIPE 和 stderr=subprocess.PIPE 表示将命令的标准输出和标准错误捕获到 PIPE 中
#         result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
#         # 使用 chardet.detect() 检测编码，然后解码
#         output_encoding = chardet.detect(result.stdout)['encoding'] or 'utf-8'
#         error_encoding = chardet.detect(result.stderr)['encoding'] or 'utf-8'
#         # 返回命令的标准输出和标准错误
#         return create_api_response(CODE_YES, '', {'output': result.stdout.decode(output_encoding, errors='replace'),
#                                                   'error': result.stderr.decode(error_encoding, errors='replace')})
#     except subprocess.CalledProcessError as e:
#         # 如果命令返回非零退出状态，返回错误信息和命令的标准输出和标准错误
#         output_encoding = chardet.detect(e.stdout)['encoding'] or 'utf-8'
#         error_encoding = chardet.detect(e.stderr)['encoding'] or 'utf-8'
#         return create_api_response(CODE_NO, 'Command returned non-zero exit status',
#                                    {'output': e.stdout.decode(output_encoding, errors='replace'),
#                                     'error': e.stderr.decode(error_encoding, errors='replace')})
#     except Exception as e:
#         # 如果运行命令时发生其他错误，返回错误信息
#         return create_api_response(CODE_NO, str(e))
