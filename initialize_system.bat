ECHO Starting system
python "Catalog\address_manager_ws.py"
ECHO Starting the Address Manager...
SLEEP 5
python "Catalog\catalog_ws.py"
ECHO Starting Catalog...
SLEEP 5
python bot.py
ECHO Starting Telegram bot...
SLEEP 10
python "Web Services\dashboard.py"
ECHO Starting Freeboard dashboard