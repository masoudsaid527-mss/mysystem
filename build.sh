set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --noinput

python manage.py makemigrations

python manage.py migrate

# if [[$CREATE_SUPERUSER]];
# then
#     python manage.py createsuperuser --noinput
# fi

if [[ "$CREATE_SUPERUSER" == "True" ]]; then
  python manage.py createsuperuser \
    --noinput \
    --username "$DJANGO_SUPERUSER_USERNAME" \
    --email "$DJANGO_SUPERUSER_EMAIL"
fi