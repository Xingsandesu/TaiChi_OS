echo "开始编译"
python3 -m nuitka --onefile --lto=yes --include-data-dir=core/html=core/html --output-dir=out --output-file=TAICHI_OS_DEV run.py
