echo "installing bena"

echo "checking your priviledges"
if [ `id -u` = 0 ]; then
	echo "you're good to go"
else
	echo "you're not cool enough to run this installer"
	exit 1
fi

APPDIR=/opt/b3na
CONFIGFILE=$APPDIR/conf/apikeys.conf

# install dependencies
./dependencies.sh

echo "creating user b3na"
getent passwd b3na > /dev/null 2&>1
if [ $? -eq 0 ]; then
	echo "b3na user already exists"
else
	useradd -M -U -G audio,sudo,dialout b3na
fi

# create app directory
if [ -d $APPDIR ]; then
	echo "appdirectory already exists."
	echo "backing up your configs to current dir"
	cp -R $APPDIR/conf/ .
	echo "deleting old copy of app"
	rm -rf $APPDIR
	echo "cloning a fresh copy"
	git clone https://github.com/armageddion/b3na.git $APPDIR
	echo "restoring your old configs"
	mv conf/ $APPDIR/
else
	git clone https://github.com/armageddion/b3na.git $APPDIR
	mkdir $APPDIR/conf

	# generate api key config file
	echo "[API KEY]" > $CONFIGFILE
	# prompt users for API keys
	echo "please enter your API key for dbip. go and get one from https://db-ip.com/api/free"
	read dbip
	if [ -z $dbip ]; then
		# user didn't provide an API key
		echo "dbip: <n/a>" >> $CONFIGFILE
	else
		echo "dbip: $dbip" >> $CONFIGFILE
	fi

	echo "please enter your API key for openWeather. go and get one from https://home.openweathermap.org/users/sign_up"
	read openWeather
	if [ -z $openWeather ]; then
		# user didn't provide an API key
		echo "openWeather: <n/a>" >> $CONFIGFILE
	else
		echo "openWeather: $openWeather" >> $CONFIGFILE	
	fi

	echo "please enter your API key for voicerss. go and get one from http://www.voicerss.org/registration.aspx"
	read voicerss
	if [ -z $voicerss ]; then
		# user didn't provide an API key
		echo "voicerss: <n/a>" >> $CONFIGFILE
	else
		echo "voicerss: $voicerss" >> $CONFIGFILE
	fi

	echo "please enter your API key for ifttt. go and get one from https://ifttt.com"
	read ifttt
	if [ -z $ifttt ]; then
		# user didn't provide an API key
		echo "ifttt_hook: <n/a>" >> $CONFIGFILE
	else
		echo "ifttt_hook: $ifttt" >> $CONFIGFILE
	fi

	echo "please enter your API key for pushbullet. go and get one from https://www.pushbullet.com/"
	read pushbullet
	if [ -z $pushbullet ]; then
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
	if [ -z $huemac ]; then
		# user didn't provide an API key
		echo "<n/a>" >> $CONFIGFILE
	else
		echo "please enter your hue developer token"
		read huetoken
		if [ -z $huetoken ]; then
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
	if [ -z $lifx ]; then
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
fi

# set up the startup file
echo "creating startup scripts"
chmod a+x ../startup/b3na
cp ../startup/b3na /etc/init.d/
update-rc.d b3na defaults

echo "creating log directory"
mkdir $APPDIR/log

echo "set up restart script"
chmod a+x $APPDIR/run/kick-b3na.sh
ln -s $APPDIR/run/kick-b3na.sh /usr/bin/kick-b3na

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

chown -R b3na:b3na $APPDIR