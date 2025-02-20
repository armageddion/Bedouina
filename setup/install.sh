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
getent passwd b3na > /dev/null 2>&1
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
		echo "dbip: None" >> $CONFIGFILE
	else
		echo "dbip: $dbip" >> $CONFIGFILE
	fi

	echo "please enter your API key for openWeather. go and get one from https://home.openweathermap.org/users/sign_up"
	read openWeather
	if [ -z $openWeather ]; then
		# user didn't provide an API key
		echo "openWeather: None" >> $CONFIGFILE
	else
		echo "openWeather: $openWeather" >> $CONFIGFILE
	fi

	echo "please enter your API key for voicerss. go and get one from http://www.voicerss.org/registration.aspx"
	read voicerss
	if [ -z $voicerss ]; then
		# user didn't provide an API key
		echo "voicerss: None" >> $CONFIGFILE
	else
		echo "voicerss: $voicerss" >> $CONFIGFILE
	fi

	echo "please enter your API key for ifttt. go and get one from https://ifttt.com"
	read ifttt
	if [ -z $ifttt ]; then
		# user didn't provide an API key
		echo "ifttt_hook: None" >> $CONFIGFILE
	else
		echo "ifttt_hook: $ifttt" >> $CONFIGFILE
	fi

	echo "please enter your API key for pushbullet. go and get one from https://www.pushbullet.com/"
	read pushbullet
	if [ -z $pushbullet ]; then
		# user didn't provide an API key
		echo "pushbullet: None" >> $CONFIGFILE
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
		echo "None" >> $CONFIGFILE
	else
		echo "please enter your hue developer token"
		read huetoken
		if [ -z $huetoken ]; then
			# user didn't provide an API key
			echo "$huemac: None" >> $CONFIGFILE
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
		echo "token: None" >> $CONFIGFILE
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
if [ -f /etc/init.d/b3na ]; then
	echo "restart script already exists"
	rm -f /etc/init.d/b3na
fi
chmod a+x $APPDIR/startup/b3na
cp $APPDIR/startup/b3na /etc/init.d/
update-rc.d b3na defaults

echo "creating log directory"
mkdir $APPDIR/log

echo "creating tmp directory"
mkdir $APPDIR/tmp

echo "set up restart script"
chmod a+x $APPDIR/run/kick-b3na.sh
if [ -f /usr/bin/kick-b3na ]; then
	echo "restart script already exists"
	rm -f /usr/bin/kick-b3na
fi
ln -s $APPDIR/run/kick-b3na.sh /usr/bin/kick-b3na

echo "set up web app startup script"
chmod a+x $APPDIR/www/b3na_web_bottle/start_web_app.sh

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

# export environment variables
export DATABASE_URL='mysql://alfr3d:alfr3d@192.168.1.100/alfr3d'
export DATABASE_NAME='alfr3d'
export DATABASE_USER='alfr3d'
export DATABASE_PSWD='alfr3d'
#more to come

echo "starting b3na service"
service b3na start

echo "creating www dir"
ln -s $APPDIR/www/ /var/www/b3na
echo "copying apache config"
cp $APPDIR/setup/b3na.conf /etc/apache2/sites-available
rm -f /etc/apache2/sites-enabled/*.conf
ln -s /etc/apache2/sites-available/b3na.conf /etc/apache2/sites-enabled/
echo "configuring apache"
service apache2 restart
