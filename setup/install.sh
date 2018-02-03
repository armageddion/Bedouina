echo "installing bena"

echo "checking your priviledges"
if [ `id -u` = 0 ]; then
	echo "you're good to go"
else
	echo "you're not cool enough to run this installer"
	exit 1
fi

APPDIR=/opt/b3na
CONFIGFILE=$APPDIR/conf

# install dependencies
./dependencies.sh

# create app directory
if [ -d $APPDIR ]; then
	echo "appdirectory already exists. deleting it."
	rm -rf $APPDIR
fi

# clone a fresh copy
echo "cloning a fresh copy"
git clone https://github.com/armageddion/b3na.git > $APPDIR

# generate api key config file
echo "[API KEY]" > $CONFIGFILE
# prompt users for API keys
echo "please enter your API key for dbip. go and get one from https://db-ip.com/api/free"
read dbip
if [[ $dbip == "" ]]; then
	# user didn't provide an API key
	echo "dbip: <n/a>" >> $CONFIGFILE
else
	echo "dbip: $dbip" >> $CONFIGFILE
fi

echo "please enter your API key for openWeather. go and get one from https://home.openweathermap.org/users/sign_up"
read openWeather
if [[ $openWeather == "" ]]; then
	# user didn't provide an API key
	echo "openWeather: <n/a>" >> $CONFIGFILE
else
	echo "openWeather: $openWeather" >> $CONFIGFILE	
fi

echo "please enter your API key for voicerss. go and get one from http://www.voicerss.org/registration.aspx"
read voicerss
if [[ $voicerss == "" ]]; then
	# user didn't provide an API key
	echo "voicerss: <n/a>" >> $CONFIGFILE
else
	echo "voicerss: $voicerss" >> $CONFIGFILE
fi

echo "please enter your API key for ifttt. go and get one from https://ifttt.com"
read ifttt
if [[ $ifttt == "" ]]; then
	# user didn't provide an API key
	echo "ifttt_hook:: <n/a>" >> $CONFIGFILE
else
	echo "ifttt_hook:: $ifttt" >> $CONFIGFILE
fi

echo "please enter your API key for pushbullet. go and get one from https://www.pushbullet.com/"
read pushbullet
if [[ $pushbullet == "" ]]; then
	# user didn't provide an API key
	echo "pushbullet: <n/a>" >> $CONFIGFILE
else
	echo "pushbullet: $pushbullet" >> $CONFIGFILE
fi

# break up the conf file
echo "" >> $CONFIGFILE
echo "[HUE dev]" >> $CONFIGFILE
echo "if you have a Phillips Hue, please enter your Hue bridge MAC address"
read huemac
if [[ $huemac == "" ]]; then
	# user didn't provide an API key
	echo "<n/a>" >> $CONFIGFILE
else
	echo "please enter your hue developer token"
	read huetoken
	if [[ $huetoken == "" ]]; then
		# user didn't provide an API key
		echo "$huemac: <n/a>" >> $CONFIGFILE	
	else
		echo "$huemac: $huetoken" >> $ CONFIGFILE
	fi
fi

# break up the conf file
echo "" >> $CONFIGFILE
echo "[Lifx]" >> $CONFIGFILE
echo "if you have any Lifx, please enter your Lifx token"
read lifx
if [[ $lifx == "" ]]; then
	# user didn't provide an API key
	echo "token: <n/a>" >> $CONFIGFILE
else
	echo "token: $lifx" >> $CONFIGFILE
fi

# TODO
echo "still need to configure access to database"
# mongo? firebase?

# TODO
echo "still need to setup client_secret.json files for gmail and calendar"

# set up the startup file
echo "creating startup scripts"
cp ../startup/b3na /etc/init.d/
update-rc.d b3na defaults

# set up logrotate
echo "setting up logrotate"
echo "$APPDIR/log/*.log {" 	> /etc/logrotate.d/b3na
echo "	su b3na b3na" 		>> /etc/logrotate.d/b3na
echo "	daily" 				>> /etc/logrotate.d/b3na
echo "	maxage 7" 			>> /etc/logrotate.d/b3na
echo "	missingok" 			>> /etc/logrotate.d/b3na
echo "	noolddir" 			>> /etc/logrotate.d/b3na
echo "	copytruncate" 		>> /etc/logrotate.d/b3na
echo "	dateext" 			>> /etc/logrotate.d/b3na
echo "	ifempty" 			>> /etc/logrotate.d/b3na
echo "}" 					>> /etc/logrotate.d/b3na