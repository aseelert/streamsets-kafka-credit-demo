# Open Kafka Broker and Controller ports
sudo firewall-cmd --permanent --add-port=9192/tcp
sudo firewall-cmd --permanent --add-port=9193/tcp

# Open Kafka UI port
sudo firewall-cmd --permanent --add-port=8180/tcp

# Open PostgreSQL ports
sudo firewall-cmd --permanent --add-port=5542/tcp
sudo firewall-cmd --permanent --add-port=5543/tcp

# Open pgAdmin port
sudo firewall-cmd --permanent --add-port=5150/tcp

# Open MinIO API and Console ports
sudo firewall-cmd --permanent --add-port=9100/tcp
sudo firewall-cmd --permanent --add-port=9101/tcp

# Open Streamsets port
sudo firewall-cmd --permanent --add-port=18631/tcp

# Reload firewall to apply changes
sudo firewall-cmd --reload

