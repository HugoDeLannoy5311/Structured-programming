import psycopg2
import collections

conn = psycopg2.connect(host="localhost", database="op=op voordeelshop", user="postgres", password="Password")
cursor = conn.cursor()

profileid = "5a393d68ed295900010384ca"


def get_all_products(profileid):
    """"
    Een functie om alle producten die een gebruiker heeft gekocht te zoeken
    Parameter: Profileid
    Returns: een lijst met productid's
    """
    cursor.execute("""SELECT session_product.productproductid FROM profile
                        JOIN browser ON profile.profileid = browser.profileprofileid JOIN "session" ON "session".browserbuid = browser.buid JOIN session_product ON session_product.sessionsessionid = "session".sessionid
                        WHERE profile.profileid = '{}' """.format(profileid))
    products = cursor.fetchall()
    return products

producten = get_all_products(profileid)
print(producten)

def meeste_zelfde(profileid_user):
    """"
    een functie om te bepalen welke gebruiker de meeste overeenkomende producten heeft gekocht
    parameter: profileid van de gebruiker
    returns: profileid van de gebruiker met de meeste overeenkomende producten
             de lijst met producten die de gebruiker zelf heeft gekocht
    """
    producten = get_all_products(profileid_user)
    profileid_freq = {}
    for product in producten:
        cursor.execute("""SELECT profile.profileid FROM profile
                            JOIN browser ON profile.profileid = browser.profileprofileid JOIN "session" ON "session".browserbuid = browser.buid JOIN session_product ON session_product.sessionsessionid = "session".sessionid
                            WHERE session_product.productproductid = '{}' AND profile.profileid != '{}' """.format(product[0], profileid_user))
        profileid_lst = cursor.fetchall()

        for profileid in profileid_lst:
            try:
                profileid_freq[profileid] += 1
            except KeyError:
                profileid_freq[profileid] = 1
            except Exception as e:
                print(e)

    gesorteerd = sorted(profileid_freq.items(), key=lambda x:x[1], reverse=True)
    print(gesorteerd)

    return gesorteerd[0][0], producten

def gebruiker_niet_bij_user(url):
    """
    een functie om te bepalen welke producten het nog meer zijn gekocht door de gebruiker die de meeste overeenkomende producten heeft
    parameters: Url van de website op poort recommendation (http://127.0.0.1:5001)
    returns: een lijst van alle producten die door de gebruiker met de meeste overeenkomende producten nog meer zijn gekocht
    """
    profileid_user = get_profileid(url)
    data = meeste_zelfde(profileid_user)
    profileid = data[0][0]
    print(profileid)
    producten_user = data[1]
    producten = get_all_products(profileid)

    producten_rec = []

    for product in producten:
        if product not in producten_user:
            producten_rec.append(product)

    print(producten_rec)

def get_profileid(url):
    """
    een funtie om de url van de website om te zetten naar het bijbehorende profileid
    parameters: Url van de website op poort recommendation (http://127.0.0.1:5001)
    returns: profileid
    """
    deel = url.split("/")
    deel.remove("GET ")
    deel.remove("4 HTTP")
    deel.remove("1.1")

    profileid = deel[0]
    return profileid



print(gebruiker_niet_bij_user("GET /5a393d68ed295900010384ca/4 HTTP/1.1"))



# print(meeste_zelfde(profileid))
#print(gebruiker_niet_bij_user(profileid))