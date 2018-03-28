#!/bin/bash

#echo "MUSIC STARTING"

#=====================================
# Account Config Stuff
#=====================================
# CLIENT_ID=""
# CLIENT_SECRET=""
REFRESH_TOKEN=""
USERNAME="armageddion@gmail.com"
KEY="$CLIENT_ID:$CLIENT_SECRET"
KEY64=$(echo -n $KEY | base64 -w 0)
REDIRECT_URI="https://example.com/callback"

#====================================
# Device Config Stuff
#==================================
PLAYLIST_ID="4tWK1DAExQ5jqfIjXEMcTS"  # Party Music
PLAYLIST_POSITION="2"
TRACK_START_TIME_MS="80000"

#================================
# Input Params
#===============================
PARTY_STATUS="$1"
ROOM="$2"

#=============================
# Other Config
#=============================
PARTY_START_TRIGGER="on"
PARTY_STOP_TRIGGER="off"

#=====================
# Start Party
#=====================

if [ "$PARTY_STATUS" == "$PARTY_START_TRIGGER" ]
then
    echo "Starting Spotify Party Script!!!"

    #===============================
    # Step 0: Set Room Device
    #===============================
    if [ "$ROOM" == "LIVINGROOM" ]
    then
        DEVICE_TO_PLAY="Jim's Echo Dot"
    elif [ "$ROOM" == "BEDROOM" ]
    then
        DEVICE_TO_PLAY="Jim's Echo"
    fi

    echo "Going To Start  On Device: $DEVICE_TO_PLAY"


    #======================================
    # Step 1: Request New Access Token
    #======================================

    ACCESS_RES=$(curl -H "Authorization: Basic $KEY64" -d grant_type=refresh_token -d refresh_token=$REFRESH_TOKEN https://accounts.spotify.com/api/token)
    echo "Got Response:"
    echo $ACCESS_RES
    ACCESS_TOKEN=$(echo $ACCESS_RES | jq .access_token)
    ACCESS_TOKEN=${ACCESS_TOKEN:1:-1}
    echo "Got Token: $ACCESS_TOKEN"

    #=======================================
    # Step 1b: Helpful for debug - list now playing
    #======================================

    echo "Currently Playing Info (before transfer):"
    curl -X GET "https://api.spotify.com/v1/me/player/currently-playing" -H "Accept: application/json" -H "Authorization: Bearer $ACCESS_TOKEN"


    #==============================
    # Step 1c: Get Device ID
    #==============================

    echo "Get list of devices:"
    curl -X GET "https://api.spotify.com/v1/me/player/devices" -H "Authorization: Bearer $ACCESS_TOKEN"
    DEVICE_RES=$(curl -X GET "https://api.spotify.com/v1/me/player/devices" -H "Authorization: Bearer $ACCESS_TOKEN")
    echo "Got Response:"
    echo $DEVICE_RES        
    DEVICE_RES=$(echo $DEVICE_RES | jq .devices)
    echo "Filtering:"
    for row in $(echo "${DEVICE_RES}" | jq -r '.[] | @base64'); do  
        _jq() {
            echo ${row} | base64 --decode | jq -r ${1}
        }

        DEVICE_NAME=$(echo $(_jq '.name'))
        if [ "$DEVICE_NAME" == "$DEVICE_TO_PLAY" ]
        then
            DEVICE_ID=$(echo $(_jq '.id'))
            echo "Going to start playing on: $DEVICE_NAME ($DEVICE_ID)"
        fi
    done  


    #=======================================
    # Step 2: Transfer Play To Echo
    #=======================================

    echo "Transfering to Echo!"
    curl -X PUT "https://api.spotify.com/v1/me/player" -H "Accept: application/json" -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" --data "{\"device_ids\":[\"$DEVICE_ID\"]}"


    #=======================================
    # Step 3: Play Playlist
    #=======================================

    echo "Playing Playlist"
    curl -X PUT "https://api.spotify.com/v1/me/player/play" -H "Accept: application/json" -H "Authorization: Bearer $ACCESS_TOKEN" -H "Content-Type: application/json" --data "{\"context_uri\":\"spotify:user:$USERNAME:playlist:$PLAYLIST_ID\",\"offset\":{\"position\":$PLAYLIST_POSITION}}"


    #=======================================
    # Step 4: Skip to position in track
    #=======================================

    echo "Moving to position in track"
    curl -X PUT "https://api.spotify.com/v1/me/player/seek?position_ms=$TRACK_START_TIME_MS&device_id=$DEVICE_ID" -H "Accept: application/json" -H "Authorization: Bearer $ACCESS_TOKEN"


    #=======================================
    # Step 5: Turn On Shuffle
    #=======================================

    curl -X PUT "https://api.spotify.com/v1/me/player/shuffle?state=true" -H "Accept: application/json" -H "Authorization: Bearer $ACCESS_TOKEN"


elif [ "$PARTY_STATUS" == "$PARTY_STOP_TRIGGER" ]
then
	echo "Stopping Party!"
        
        #======================================
        # Step 1: Request New Access Token
        #======================================

        ACCESS_RES=$(curl -H "Authorization: Basic $KEY64" -d grant_type=refresh_token -d refresh_token=$REFRESH_TOKEN https://accounts.spotify.com/api/token)
        echo "Got Response:"
        echo $ACCESS_RES
        ACCESS_TOKEN=$(echo $ACCESS_RES | jq .access_token)
        ACCESS_TOKEN=${ACCESS_TOKEN:1:-1}
        echo "Got Token: $ACCESS_TOKEN"


        #======================================
        # Step 2: Pause Music
        #======================================

        curl -X PUT "https://api.spotify.com/v1/me/player/pause" -H "Accept: application/json" -H "Authorization: Bearer $ACCESS_TOKEN" 

fi


