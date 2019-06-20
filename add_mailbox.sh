#!/bin/bash
#set -x

HOME=/home
SHL=/bin/false

if getent passwd @option.customer_name@ > /dev/null 2>&1; then
    echo "@option.customer_name@ exists"
    exit 1
else

if [ @option.customer_name@ < /dev/null ];
then
user=$(echo @option.customer_name@ | awk '{$1=$1};1')
pass=$(apg -n1 -m 11 -x 12 -M SNCL)
sudo /usr/sbin/useradd -d $HOME/$user -m -g users -s $SHL $user
sudo /bin/chmod 0700 $HOME/$user

echo $user:$pass | sudo chpasswd
echo "Username is $user, Password is $pass"
fi
fi
