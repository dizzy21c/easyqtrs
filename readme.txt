sudo apt-get update
sudo apt-get install python3-dev
# 装talib前要先装numpy
python3.6 -m pip install numpy -i https://pypi.doubanio.com/simple
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzvf ta-lib-0.4.0-src.tar.gz
cd ta-lib
./configure --prefix=/usr
make
sudo make install
cd ..
pip install TA-Lib
