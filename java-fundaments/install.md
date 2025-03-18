sudo dnf install java-17-openjdk java-17-openjdk-devel -y

- Instalación Manual

sudo dnf -y install curl wget -y 
wget https://download.java.net/java/GA/jdk17.0.2/dfd4a8d0985749f896bed50d7138ee7f/8/GPL/openjdk-17.0.2_linux-x64_bin.tar.gz

tar xvf openjdk-17.0.2_linux-x64_bin.tar.gz

sudo mv jdk-17.0.2 /opt/

sudo tee /etc/profile.d/jdk17.sh <<EOF
export JAVA_HOME=/opt/jdk-17.0.2
export PATH=\$PATH:\$JAVA_HOME/bin
EOF

source /etc/profile.d/jdk17.sh

[https://computingforgeeks.com/install-oracle-java-openjdk-fedora-linux/] 


o se puedan usar un gestiòn de versiones jenv