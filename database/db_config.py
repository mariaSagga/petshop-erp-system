import psycopg2

def get_db_connection():

    connection = psycopg2.connect(
        host="dpg-d8aq85f7f7vs73ddg9f0-a",
        database="erp_ecommerce",
        user="petshop_user",
        password="fOzoicXlrsNZG5fZaEq4Gylvh5KX37Ku",
        port="5432"
    )

    return connection