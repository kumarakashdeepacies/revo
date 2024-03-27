echo -e "\e[1;32m---Kepler Deployment---\e[0m"
echo ""
# Installing Stuff

# Python, Redis, nginx installation
echo -e "\e[1;32mInstalling Python\e[0m"
sudo apt remove python3-apt
sudo apt autoremove
sudo apt autoclean
sudo apt install python3-apt

sudo apt update
sudo apt install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8
alias python=/usr/bin/python3.8
source ~/.bashrc
python --version
echo -e "\e[1;32mPython installation complete\e[0m"

echo -e "\e[1;32mInstalling redis\e[0m"
sudo apt-get install redis-server
sudo systemctl enable redis-server.service
echo -e "\e[1;32mRedis installation complete\e[0m"

echo -e "\e[1;32mInstalling nginx\e[0m"
sudo apt install nginx
echo -e "\e[1;32mnginx installation complete\e[0m"

#Install development libraries necessary for installation

#Microsoft ODBC driver installation
echo -e "\e[1;32mMicrosoft ODBC driver installation\e[0m"
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install -y msodbcsql17
sudo ACCEPT_EULA=Y apt-get install -y mssql-tools
echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
source ~/.bashrc
sudo apt-get install -y unixodbc-dev

echo -e "\e[1;32mMicrosoft ODBC installation done\e[0m"

#Create project directory and move requirements.txt
echo -e "\e[1;32mCreate project Directory\e[0m"

echo -e "\e[1;32mDirectory Created\e[0m"

#Unpack installation folders
echo -e "\e[1;32mUnpack installation folders\e[0m"
# Update with folder where installation is to be done and Revolutio installation zip is available
cd /home
# Update with folder where installation is to be done and Revolutio installation zip is available
mkdir Revolutio
git clone https://aciesconsulting@dev.azure.com/aciesconsulting/Revolutio/_git/Revolutio
cd Revolutio/
mkdir logs
mkdir run
echo -e "\e[1;32mApplication unpacked\e[0m"

#Create venv
echo -e "\e[1;32mCreating Venv\e[0m"
alias python=/usr/bin/python3.8
source ~/.bashrc
python --version
python3.8 -m venv rev_venv

echo -e "\e[1;32mActivating Venv\e[0m"
source rev_venv/bin/activate

#Install python libraries
echo -e "\e[1;32mInstalling requirements.txt\e[0m"
pip install -r requirements/base.txt
pip install --no-cache ./Installation_ref/djangocodemirror-2.1.0-py2.py3-none-any.whl
echo -e "\e[1;32mDependent library installations completed\e[0m"

echo -e "\e[1;32mUpdate DB credentials in /Revolutio/config/settings/base.py\e[0m"
echo -e "\e[1;32mUpdate DB credentials in /Revolutio/Installation_ref/revolutio.service\e[0m"
echo "Have you updated DB credentials and revolutio folder location? [Y/N]"; read input;
if [ "$input" == "Y" ];

then echo "Proceeding with application initiation";
sudo rm /etc/nginx/nginx.conf;
sudo cp ./Installation_ref/revolutio.service /etc/systemd/system/revolutio.service;
sudo cp ./Installation_ref/nginx.conf /etc/nginx/nginx.conf;
echo -e "\e[1;32mStarting nginx\e[0m"
sudo systemctl start revolutio.service
sudo systemctl enable revolutio.service
sudo systemctl start nginx
sudo systemctl enable nginx

else echo "Continue after updating DB credentials and Revolutio folder location";fi

echo -e "\e[1;32mDone\e[0m"