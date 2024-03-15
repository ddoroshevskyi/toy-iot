## Симулятор IoT термометра | IoT thermometer simulator
Компаньйон до [курсу з автоматизації тестів](https://github.com/ddoroshevskyi/test-automation-roadmap).
Ідея в тому, щоб використовувати цю програму в якості продукту для якого потрібно написати тестовий фреймворк та тести.

Companion piece to [my test automation course](https://github.com/ddoroshevskyi/test-automation-roadmap).
The idea is to practice what the students learned in the course using this program.

## Запуск у Docker | Run in Docker
```
git clone https://github.com/ddoroshevskyi/toy-iot.git
cd toy-iot
docker build -t sensor .
docker run --rm -p 9898:9898 sensor
```

## Запуск напряму | Run in Python
```
git clone https://github.com/ddoroshevskyi/toy-iot.git
cd toy-iot
pip install -r requirements.txt
python -m aiohttp.web -H localhost -P 9898 sensor:init_func
```

## API
Сенсор має [JSON-RPC](https://www.jsonrpc.org/specification) API.

### Методи | Methods
Методи доступні на `http:0.0.0.0:9898/rpc` (Docker) або `http://127.0.0.1:9898/rpc` (локально). Щоб побачити повний список методів та їх параметрів, відправте запит:

Methods are available at `http:0.0.0.0:9898/rpc` (Docker) or `http://127.0.0.1/rpc` (locally). In order to see the full list of methods and their arguments, make the following request:
```
curl -X POST http://0.0.0.0:9898/rpc -d '{"method": "get_methods", "jsonrpc": "2.0", "id": 1}'

{"jsonrpc": "2.0", "id": 1, "result": [{"get_info": []}, {"get_methods": []}, {"set_name": ["name"]}, {"set_reading_interval": ["interval"]}, {"reset_to_factory": []}, {"update_firmware": []}, {"reboot": []}, {"get_reading": []}]}
```
