"""
Seja bem vindo à documentação da API do Formaplus!

Este projeto é escrito em Python, com o
[Flask](https://flask.palletsprojects.com/) framework web. Esta documentação é gerada automaticamente pelo
[código fonte do projeto](https://github.com/wadsongarbes/formaplus-api) usando
a extensão de flask [APIFairy](https://github.com/miguelgrinberg/apifairy).

## Introdução

A API Formaplus é ideal para a criação de questões de prova. Seu uso pode-se extender a um
framework de front-end web, mobile ou simplesmente pode ser consumido puro, 

Microblog API provides all the base features required to implement a
microblogging project:

- Registro de usuários, login e logout
- Fluxo de recuperação de senha com emails
- Criação e deleção de questões creation and deletion
- Paginação
- Opção de desabilitar a autenticação durante o desenvolvimento

## Configuração

Se você está rodando a API Formaplus enquanto desenvolve um frontend,
pode configurar uma série de variáveis de ambiente para ajudar no processo. 
Estas variáveis podem ser definidas diretamente no ambiente ou podem ser passadas em um arquivo
`.env` no diretório do projeto. A seguir, há uma tabela contendo as variáveis que podem
ser utilizadas neste projeto.

| Variável de ambiente | Padrão | Descrição |
| - | - | - |
| `SECRET_KEY` | `top-secret!` | Chave secreta para ser usada em tokens |
| `DATABASE_URL`  | `sqlite:///db.sqlite` | A URL do banco de dados, definida pelo framework [SQLAlchemy](https://docs.sqlalchemy.org/en/14/core/engines.html#database-urls). |
| `SQL_ECHO` | não definida | Define se será impresso no terminal instruções SQL (útil para debug). |
| `DISABLE_AUTH` | não definida | Define se haverá ou não autenticação na aplicação. Quando desativada, assume que o user cujo `id=1` deve existir no banco de dados. |
| `ACCESS_TOKEN_MINUTES` | `15` | Validade do token de acesso em minutos. |
| `REFRESH_TOKEN_DAYS` | `7` | Número de dias em que o token de refresh é válido. |
| `REFRESH_TOKEN_IN_COOKIE` | `yes` | Define se o token pode ser retornado em um cookie seguro. |
| `REFRESH_TOKEN_IN_BODY' | `no` | Define se o refresh token virá no campo body. |
| `RESET_TOKEN_MINUTES` | `15` | Número de minutos em que o token de reset é válido. |
| `PASSWORD_RESET_URL` | `http://localhost:3000/reset` | A URL que será usada nos links de reseção de senha. |
| `USE_CORS` | `yes` | Define se o CORS será suportado ou não, podendo ser configurável de acordo com a extensão flask-CORS. |
| `DOCS_UI` | `elements` | Interface da documentação. Os valores permitidos são `swagger_ui`, `redoc`, `rapidoc` e `elements`. |
| `MAIL_SERVER` | `localhost` | O servidor de email a ser utilizado para o envio de emails. |
| `MAIL_PORT` | `25` | A porta utilizado pelo serviço de emails. |
| `MAIL_USE_TLS` | não definida | Define se havera TLS ou não no serviço de envio de emails. |
| `MAIL_USERNAME` | não definida | O usuário utilizado pelo serviço de envio de emails. |
| `MAIL_PASSWORD` | não definida | A senha correspondente ao usuário utilizador do serviço de emails. |
| `MAIL_DEFAULT_SENDER` | `nao-responda@formaplus.com.br` | Endereço padrão para envio de emails. |

## Autenticação

The authentication flow for this API is based on *access* and *refresh*
tokens.

To obtain an access and refresh token pair, the client must send a `POST`
request to the `/api/tokens` endpoint, passing the username and password of
the user in a `Authorization` header, according to HTTP Basic Authentication
scheme. The response includes the access and refresh tokens in the body. For
added security in single-page applications, the refresh token is also returned
in a secure cookie.

Most endpoints in this API are authenticated with the access token, passed
in the `Authorization` header, using the `Bearer` scheme.

Access tokens are valid for 15 minutes (by default) from the time they are
issued. When the access token is expired, the client can renew it using the
refresh token. For this, the client must send a `PUT` request to the
`/api/tokens` endpoint, passing the expired access token in the body of the
request, and the refresh token either in the body, or through the secure cookie
sent when the tokens were requested. The response to this request will include
a new pair of tokens. Refresh tokens have a default validity period of 7 days,
and can only be used to renew the access token they were returned with. An
attempt to use a refresh token more than once is considered a possible attack,
and will cause all existing tokens for the user to be revoked immediately as a
mitigation measure.

All authentication failures are handled with a `401` status code in the
response.

### Password Resets

This API supports a password reset flow, to help users who forget their
passwords regain access to their accounts. To issue a password reset request,
the client must send a `POST` request to `/api/tokens/reset`, passing the
user's email in the body of the request. The user will receive a password reset
link by email, based on the password reset URL entered in the configuration
and a `token` query string paramter set to an email reset token, with a
validity of 15 minutes.

When the user clicks on the password reset link, the client application must
capture the `token` query string argument and send it in a `PUT` request to
`/api/tokens/reset`, along with the new password chosen by the user.

## Pagination

API endpoints that return collections of resources, such as the users or posts,
implement pagination, and the client must use query string arguments to specify
the range of items to return.

The number of items to return is specified by the `limit` argument, which is
optional. If not specified, the server sets the limit to a reasonable value for
the endpoint. If the limit is too large, the server may decide to use a lower
value instead. The following example shows how to request the first 10 users:

    http://localhost:5000/api/users?limit=10

The `offset` argument is used to specify the zero-based index of the first item
to return. If not given, the server sets the offset to 0. The following example
shows how to request the second page of users with a page size of 10:

    http://localhost:5000/api/users?limit=10&offset=10

Sometimes paginating with the `offset` argument can be inconvenient, such as
with collections where new elements are not always inserted at the end of the
list. As an alternative to `offset`, the `after` argument can be used to set
the start item to the item after the one specified. This API supports `after`
for collections of blog posts, which are sorted by their publication time in
descending order, and for collections of users, which are sorted by their
username in ascending order. For blog posts, the `after` argument must be set
to a date and time specification in ISO 8601 format, such as
`2020-01-01T00:00:00Z`. For users, the `after` argument must be set to a
string. Examples:

    http://localhost:5000/api/posts?limit=10&after=2021-01-01T00:00:00
    http://localhost:5000/api/users/me/followers?limit=10&after=diana

The response body in a paginated request contains a `data` attribute that is
set to the list of entities that are in the requested page. A `pagination`
attribute is also included with `offset`, `limit`, `count` and `total`
sub-attributes, which should enable the client to present pagination controls
to the user.

## Errors

All errors returned by this API use the following JSON structure:

```json
{
    "code": <numeric error code>,
    "message": <short error message>,
    "description": <longer error description>,
}
```

In the case of schema validation errors, an `errors` property is also returned,
containing a detailed list of validation errors found in the submitted request:

```json
{
    "code": <error code>,
    "message": <error message>,
    "description": <error description>,
    "errors": [ <error details>, ... ]
}
```
"""  # noqa: E501

from api.app import create_app, db, ma  # noqa: F401
