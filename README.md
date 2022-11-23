# AlphaESS connector

Script to store AlphaESS readings via ModBus to MySQL

Uses [alphaess-modbus](https://github.com/SorX14/alphaess-modbus) to retrieve ModBus registers from a connected AlphaESS inverter.

## Installation and usage

Clones, setup up virtualenv and prepares configuration file

``` bash
git clone https://github.com/SorX14/alphaess_collector.git
cd ./alphaess_collector
python -m venv .
./bin/activate
python -m pip install -r requirements.txt
cp config.ini.dist config.ini
```

Update `config.ini` with your database details. 

Database assumes the following schema:

``` sql
CREATE TABLE `solar` (
  `id` int NOT NULL AUTO_INCREMENT,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  `pv` int DEFAULT NULL,
  `grid` int DEFAULT NULL,
  `load` int DEFAULT NULL,
  `voltage` float DEFAULT NULL,
  `frequency` float DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;
```

Run with:

```
./bin/python3 ./collector.py
```

## Run at boot

Assumes using raspbian.

Optionally install `systemd` service to run at boot:

Modify `pv-collector.service` to use the correct directory (change `srv/alpha-client` to your directory)

```
sudo ln -s ./pv-collector.service /lib/systemd/system/pv-collector.service
sudo chmod 644 /lib/systemd/system/pv-collector.service
sudo systemctl daemon-reload
sudo systemctl enable pv-collector.service
sudo systemctl start pv-collector.service
```