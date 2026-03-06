pip install -r requirements.txt --break-system-packages --root-user-action=ignore
python manage.py collectstatic --noinput

mkdir -p staticfiles_build/static
cp -r staticfiles/* staticfiles_build/static/