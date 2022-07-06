#!/bin/bash

[[ $(id -u) != 0 ]] && echo -e "Execute esse script com permissao de root" && exit 1
[[ -d /etc/tron_ssh ]] && rm -rf /etc/tron_ssh

for pkt in git pip3; do
    if ! which $pkt &>/dev/null; then
        echo -ne "Instalando $pkt... "
        apt-get install $pkt &>/dev/null
        echo -e 'Ok'
    fi
done

echo -e "Cloando projeto..."
git clone https://github.com/c0n3ct4r/tron_ssh.git &>/dev/null
echo -e "Instalando requirimentos..."
pip3 install -r tron_ssh/requirements.txt &>/dev/null
chmod +x tron_ssh/tron
mv tron_ssh/tron /bin
mv tron_ssh/tron_ssh /etc
echo -e "Instalacao efetuada com sucesso"
echo -e "Execute: tron"
