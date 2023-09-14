### export the python path to the root of the folder.  ###
export PYTHONPATH="/home/ec2-user/algo-trade/algo-trade-sqllite"

### Install all libraries
#pip install -r requirements.txt

### generate the access token key and store it to json file. ###
python src/script/auth_token.py

### save the previous data to csv and truncate the table for fresh new entries. ###
python src/script/save_data.py

### Unlock the databse
#python database/database_helper.py

### start storing the data in real time streaming to database. ###
python src/script/store_data.py