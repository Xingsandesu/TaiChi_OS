#！/bin/bash
echo "系统更新"
sudo apt update
echo "安装依赖"
sudo apt install build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev wget libbz2-dev patchelf htop clang
echo "解压Python源码"
tar -zvxf Python-3.11.7.tgz
echo "编译安装Python"
cd Python-3.11.7
echo "Python源码lto优化"
./configure --enable-optimizations --prefix=/usr/taichi/python
echo "Python源码编译"
make
echo "Python源码编译"
make install
echo "安装软件依赖"
cd ..
pip3 install -r requirements.txt
echo "安装nuitka"
pip3 install nuitka
echo "开始编译"
python3 -m nuitka --onefile --clang --include-data-dir=core/html=core/html --output-dir=out --output-file=TAICHI_OS_ARM64 run.py
echo "打包软件"
tar -czvf TAICHI_OS_ARM64_0.9.7.tar.gz out/TAICHI_OS_ARM64
