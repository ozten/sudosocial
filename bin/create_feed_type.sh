echo "Creating files for $1"
mkdir templates/${1}
mkdir lifestream/${1}

cp templates/generic/entry.html templates/${1}/
cp -Rf lifestream/generic/*.py lifestream/${1}
echo "Edit lifestream/views.py and update websiteFeedType with a regexp"