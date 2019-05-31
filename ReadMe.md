# HTTP_client
Консольное приложение для получения данных по HTTP.

## Параметры запуска
* `--help [-h]` - Справка по использованию программы.
* `--uri [-u]` - Обязательным именнованным аргументом вводится URI, с которого необходимо получить данные. Допускается использование "http://"<br />
* `--method [-m]` - Обязательным именнованным аргументом вводится метод запроса {GET|PUT|POST|HEAD|OPTIONS|DELETE}.<br />
Примеры: `-u example.org -m GET`, `-u http://example.com -m GET`
* `--header [-hd]` - Необязательным именнованным аргументом вводится заголовок(и) запроса. Каждый заголовок пишется внутри двойных кавычек!
* `--body [-b]` - Необязательным именнованным аргументом вводится тело запроса запроса. Тело запроса пишется внутри двойных кавычек!

## Использование
(os Windows10)<br />
Программа запускается в командной строке с обязательными параметрами `--uri` и `--method`:<br />
> C:\HTTP_client>python HTTP_client.py --uri example.org -m GET

Далее клиент вернет html вариант ответа в файл `received.html`, либо ошибку
## Автор
Калугин Павел, Апрель 2019
## Контакты
e-mail: pkalugin48@gmail.com