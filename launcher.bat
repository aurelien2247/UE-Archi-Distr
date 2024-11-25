@echo off
echo Lancement du service Movie...
cd movie
pip install -r requirements.txt
start python movie.py
cd ..

echo Lancement du service Showtime...
cd showtime
pip install -r requirements.txt
python -m grpc_tools.protoc --proto_path=./protos --python_out=. --grpc_python_out=. showtime.proto
start python showtime.py
cd ..

echo Lancement du service Booking...
cd booking
pip install -r requirements.txt
python -m grpc_tools.protoc --proto_path=./protos --python_out=. --grpc_python_out=. booking.proto
start python booking.py
cd ..

echo Lancement du service User...
cd user
pip install -r requirements.txt
start python user.py
cd ..

echo Tous les services ont été lancés !
pause