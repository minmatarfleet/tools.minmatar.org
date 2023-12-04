from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

WIKI_JS_API_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOjEsImdycCI6MSwiaWF0IjoxNzAxNjE2NjU3LCJleHAiOjE3OTYyODk0NTcsImF1ZCI6InVybjp3aWtpLmpzIiwiaXNzIjoidXJuOndpa2kuanMifQ.wLE5JLAqf8JeTHDjZQPdInKi701f6lG97vl30urHEF7K2jL-oX_jWoFW8KvhWu9o46PwxtD4PwYieV3k90qU_TmgtZZUoM8UDZB7rRCtXmuUw3r-pn0Uq44AiJOrh3IVgYH4btOz0MpvBXmbp3mWOh3wLZM5Y7vt4oJEGRv5oUivpBUl6TN34kWs2rCgqjfz7MxYyAdGfDLEBBL5BlGhDGAVcE3rr1obQHjNEoe_jtd9521wTiiL6o9ro4IoAZ9ScgCte14FrEVgDdaAlF1fiOnUU0d-6dfivaZ6RyLqXtUOw81AXwSHaHYqMweanSOlPhL0lg8n9tCVRSs1zQOKXQ"

client = Client(
    transport=RequestsHTTPTransport(
        url="https://wiki.minmatar.org/graphql",
        headers={
            'Authorization': 'Bearer ' + WIKI_JS_API_KEY
        }
    )
)


def get_users():
    query = gql('''
        query {
            users {
                list {
                    id
                    name
                    email
                    providerKey
                }
            }
        }
    ''')
    return client.execute(query)


print(get_users())
