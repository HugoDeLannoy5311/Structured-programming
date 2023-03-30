import psycopg2
import collections

conn = psycopg2.connect(host="localhost", database="op=op voordeelshop", user="postgres", password="Password")
cursor = conn.cursor()

productid = 2583

def get_product_data(productid):
    """
    functie die de basale informatie ophaalt van een product
    parameter: productid
    returns: category, sub category, sub sub category en selling price
    """
    cursor.execute("""SELECT category, sub_category, sub_sub_category, selling_price FROM product WHERE productid = '{}';""".format(productid))
    category = cursor.fetchall()
    return category

#print(get_product_data(productid))


def url_website(url):
    """"
    functie die de url van de website omzet in een productid en de daaruitvolgende informatie
    of een bezochte category, in dit geval blijft de selling price: None
    parameter: URL van de website op poort http://127.0.0.1:5000
    Returns: productid, category, sub_category, sub_sub_category, selling_price
    """
    productid = None
    category = None
    sub_category = None
    sub_sub_category = None
    selling_price = None
    max_price = None
    min_price = None

    print(url)
    deel = url.split("/")
    print(deel)
    deel.remove("GET ")
    deel.remove(" HTTP")
    deel.remove("1.1")

    if deel[0] == "producten":                           #als er in de url "producten" staat ben je een categorie pagina aan het bezoeken
        deel.remove("producten")
        cursor.execute("""SELECT DISTINCT category FROM product""")
        category_aanwezig = cursor.fetchall()
        cursor.execute("""SELECT DISTINCT sub_category FROM product""")
        sub_category_aanwezig = cursor.fetchall()
        cursor.execute("""SELECT DISTINCT sub_sub_category FROM product""")
        sub_sub_category_aanwezig = cursor.fetchall()

        categorys = []
        for element in deel:
            el = element
            cat = el.capitalize()
            categorys.append(cat)

        if len(categorys) > 2:
            for i in range(len(sub_sub_category_aanwezig)):
                if sub_sub_category_aanwezig[i][0] != None:
                    if sub_sub_category_aanwezig[i][0][0:3] == categorys[2][0:3]:
                        sub_sub_category = sub_sub_category_aanwezig[i][0]
        if len(categorys) > 1:
            for i in range(len(sub_category_aanwezig)):
                if sub_category_aanwezig[i][0] != None:
                    if sub_category_aanwezig[i][0][0:3] == categorys[1][0:3]:
                        sub_category = sub_category_aanwezig[i][0]
        if len(categorys) > 0:
            for i in range(len(category_aanwezig)):
                if category_aanwezig[i][0] != None:
                    if category_aanwezig[i][0][0:3] == categorys[0][0:3]:
                        category = category_aanwezig[i][0]

    if deel[0] == "productdetail":              #als er in de url "productdetail" staat ben je een product aan het bezoeken
        heel = deel[1]                          #en kunnen we een productid en de bebehorende info herleiden
        productid = (heel.split("'")[1]).split("'")[0]
        product_data = get_product_data(productid)
        print(product_data[0])
        category = product_data[0][0]
        sub_category = product_data[0][1]
        sub_sub_category = product_data[0][2]
        selling_price = product_data[0][3]
        print(product_data)

        price_range = 0.7
        max_price = selling_price / price_range
        min_price = selling_price * price_range
        print(selling_price, min_price, max_price)

    #print("data:", category, sub_category, sub_sub_category, selling_price)
    return productid, category, sub_category, sub_sub_category, selling_price, max_price, min_price



def top_sales_product_category(productdata):
    """"
    Een functie die bepaalt wat het meest verkochte product is dat voldoet aan de opgegeven parameters, indien er een aantal ontbreken word hier None aangenomen en tellen alle categorien mee
    parameters: productid, category, sub_category, sub_sub_category, selling_price. Deze kunnen: None zijn
    Returns: Een list van de 5 meest verkochte producten die aan de opgegeven parameters voldoen
    """

    productid = productdata[0]
    category = productdata[1]
    sub_category = productdata[2]
    sub_sub_category = productdata[3]
    selling_price = productdata[4]
    max_price = productdata[5]
    min_price = productdata[6]

    if selling_price != None:                       # als er een selling price is word deze meegenomen
        if category != None:                        #hetzelfde geld voor de category, sub_category en sub_sub_category
            if sub_category != None:
                if sub_sub_category != None:
                    cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category  
                                                    FROM session_product 
                                                    JOIN product ON product.productid = session_product.productproductid
                                                    WHERE product.category = '{}' AND product.sub_category = '{}' AND product.sub_sub_category = '{}' AND product.selling_price < {} AND product.selling_price > {}
                                                    GROUP BY session_product.productproductid, product.productid
                                                    ORDER BY COUNT(productproductid) DESC """.format(category,
                                                                                                     sub_category,
                                                                                                     sub_sub_category,
                                                                                                     max_price,
                                                                                                     min_price))
                else:
                    cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category  
                                                                    FROM session_product 
                                                                    JOIN product ON product.productid = session_product.productproductid
                                                                    WHERE product.category = '{}' AND product.sub_category = '{}' AND product.selling_price < {} AND product.selling_price > {}
                                                                    GROUP BY session_product.productproductid, product.productid
                                                                    ORDER BY COUNT(productproductid) DESC """.format(
                        category, sub_category, max_price, min_price))
            else:
                cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category  
                                                                FROM session_product 
                                                                JOIN product ON product.productid = session_product.productproductid
                                                                WHERE product.category = '{}' AND product.selling_price < {} AND product.selling_price > {}
                                                                GROUP BY session_product.productproductid, product.productid
                                                                ORDER BY COUNT(productproductid) DESC """.format(
                    category, max_price, min_price))
        else:
            cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category 
                                                                        FROM session_product 
                                                                        JOIN product ON product.productid = session_product.productproductid
                                                                        WHERE product.selling_price < {} AND product.selling_price > {}
                                                                        GROUP BY session_product.productproductid, product.productid
                                                                        ORDER BY COUNT(productproductid) DESC """.format(
                max_price, min_price))
    else:                                    # als er geen selling price is word deze niet meegenomen
        if category != None:                    #hetzelfde geld voor de category, sub_category en sub_sub_category
            if sub_category != None:
                if sub_sub_category != None:
                    cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category  
                                                           FROM session_product 
                                                           JOIN product ON product.productid = session_product.productproductid
                                                           WHERE product.category = '{}' AND product.sub_category = '{}' AND product.sub_sub_category = '{}' 
                                                           GROUP BY session_product.productproductid, product.productid
                                                           ORDER BY COUNT(productproductid) DESC """.format(category,
                                                                                                            sub_category,
                                                                                                            sub_sub_category))
                else:
                    cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category  
                                                                           FROM session_product 
                                                                           JOIN product ON product.productid = session_product.productproductid
                                                                           WHERE product.category = '{}' AND product.sub_category = '{}' 
                                                                           GROUP BY session_product.productproductid, product.productid
                                                                           ORDER BY COUNT(productproductid) DESC """.format(
                        category, sub_category))
            else:
                cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category  
                                                                       FROM session_product 
                                                                       JOIN product ON product.productid = session_product.productproductid
                                                                       WHERE product.category = '{}' 
                                                                       GROUP BY session_product.productproductid, product.productid
                                                                       ORDER BY COUNT(productproductid) DESC """.format(
                    category))
        else:
            cursor.execute("""SELECT COUNT(session_product.productproductid) AS "aantal", session_product.productproductid, product.category, product.selling_price, product.sub_category, product.sub_sub_category 
                                                                               FROM session_product 
                                                                               JOIN product ON product.productid = session_product.productproductid
                                                                               GROUP BY session_product.productproductid, product.productid
                                                                               ORDER BY COUNT(productproductid) DESC """)

    top_sales = cursor.fetchall()               #data komt gesorteerd op grootste eerst uit de query
    teller = 0
    product_rec_list = []
    for product in top_sales:
        teller += 1
        print(product[1])
        if product[1] != productid:             #het product wat aanbevolen word mag niet het product zijn dat je op dit moment aan het bezoeken bent
            print(product)
            product_rec_list.append(product[1])
        if teller == 5:
            return "recommendations: ",product_rec_list           #returnt een list van de 5 producten



print(top_sales_product_category(url_website("GET /producten/huishouden/toilet-en-keuken/ HTTP/1.1")))





#print(top_sales_product_category("GET /producten/gezond-en-verzorging/ HTTP/1.1"))

#print(top_sales_product_category("GET /producten/huishouden/toilet-en-keuken/ HTTP/1.1"))



def alle_producten():
    """
    een functie om de andere funties te testen
    NIET BELANGRIJK VOOR DE OPDRACHT
    """

    cursor.execute("""SELECT * FROM product
                        WHERE category is not NULL AND sub_category is not NULL AND sub_sub_category is NULL""")
    producten = cursor.fetchall()
    x = 0
    for product in producten:
        print(top_sales_product_category(url_website("GET /productdetail/{}/ HTTP/1.1".format(product))))
        if x > 200:
            break
        x += 1


#alle_producten()

cursor.close()
conn.close()
