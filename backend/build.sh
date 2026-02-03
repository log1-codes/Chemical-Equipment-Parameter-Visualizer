set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate
python init_db.py
