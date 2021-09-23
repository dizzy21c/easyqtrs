#g++ -std=c++11 -shared -fPIC -o chanlunx.so Main.cpp ZhongShu.cpp KxianChuLi.cpp Duan.cpp BiChuLi.cpp Bi.cpp
g++ -shared -fPIC -fvisibility=hidden -o chanlun.so Main.cpp ChanlunCore.cpp