Report-app startup flow:

cd D:\my-app\report-app
.\venv\Scripts\activate
python app.py

Typical workflow after you change code locally:
#See what changed.
git status

#Stage changes.
git add .

#Save changes locally.
git commit -m "Describe what changed"

#Upload changes to GitHub.
git push

#To pull changes from GitHub to another machine
git pull