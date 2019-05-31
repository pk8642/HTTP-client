# HTTP_client
Консольное приложение для получения данных по HTTP.

## Параметры запуска
* `--help [-h]` - Справка по использованию программы.
* `--uri [-u]` - Обязательным именнованным аргументом вводится URI, с которого необходимо получить данные. Допускается использование "http://"  
* `--method [-m]` - Обязательным именнованным аргументом вводится метод запроса `{GET|PUT|POST|HEAD|OPTIONS|DELETE}`.  
Примеры: `-u example.org -m GET`, `-u http://example.com -m GET`  
* `--header [-hd]` - Необязательным именнованным аргументом вводится заголовок(и) запроса. Каждый заголовок пишется внутри двойных кавычек!  
* `--body [-b]` - Необязательным именнованным аргументом вводится тело запроса запроса. Тело запроса пишется внутри двойных кавычек!  
* `--timeout [-to]` - Необязательным именованным аргументом вводится время ожидания в секундах ответа от сервера.  
* `--close [-cls]` - Для завершения сессии вводится данный аргумент. Закрывает сокет, через который происходило подключение.

## Использование
(os Windows10)  
Программа запускается в командной строке с обязательными параметрами `--uri [-u]` и `--method [-m]`:  
> C:\HTTP_client>python HTTP_client.py --uri example.org -m GET

Далее клиент вернет ответ в файл `received` с расширением загружаемого документа, после чего можно продолжать делать необходимые запросы
## Автор
Калугин Павел, Апрель 2019
## Контакты
e-mail: pkalugin48@gmail.com