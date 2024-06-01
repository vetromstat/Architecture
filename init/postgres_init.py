import random
import string
from sqlalchemy import create_engine, inspect, MetaData, Table, Column, Integer, String, Index
from sqlalchemy.orm import sessionmaker


def create_tables(table_name):
    users = Table(
        table_name, metadata,
        Column('id', Integer, primary_key=True,autoincrement=True),
        Column('login', String(255),unique=True),
        Column('password', String(255)),
        Column('first_name', String(255)),
        Column('last_name', String(255)),
        Column('address', String(255)),
    )
    metadata.create_all(engine)
    Index('id_index', users.c.id)
    Index('login_index', users.c.login)
    Index('first_name_index', users.c.first_name)
    Index('last_name_index', users.c.last_name)
    Index('address_index', users.c.address)
    print(f"Table {table_name} created")


def insert_data(data, table_name):
    session = Session()
    table = metadata.tables[table_name]
    session.execute(table.insert(), data)
    session.commit()
    session.close()


def delete_table(table_name):
    metadata.reflect(bind=engine)
    if table_name in metadata.tables:
        table = metadata.tables[table_name]
        table.drop(bind=engine)
        metadata.clear()
        print(f"Table {table_name} was dropped")
    else:
        print(f"Table {table_name} not found")


def generate_random_data(num_users):
    users_data = []
    for i in range(num_users):
        login = ''.join(random.choices(string.ascii_letters, k=10))
        password = ''.join(random.choices(string.ascii_letters, k=10))
        first_name = ''.join(random.choices(string.ascii_letters, k=10))
        last_name = ''.join(random.choices(string.ascii_letters, k=10))
        address = ''.join(random.choices(string.ascii_letters, k=20))
        users_data.append({
            'id': i,
            'login': login,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'address': address
        })
    return users_data


def init_database(table_name, num_users=1):
    inspector = inspect(engine)
    if inspector.has_table(table_name):
        delete_table(table_name)
    print("Initialize DB")
    create_tables(table_name)
    users_data = generate_random_data(num_users)
    print("Inserted data: " + str(users_data))
    insert_data(users_data, table_name)


if __name__ == "__main__":
    engine = create_engine(
        'postgresql://postgres:postgres@postgres:5432/archdb')
    metadata = MetaData()
    metadata.bind = engine
    Session = sessionmaker(bind=engine)
    init_database("users")
    print("succes")
