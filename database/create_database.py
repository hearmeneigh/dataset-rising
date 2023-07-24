from utils.db_utils import connect_to_db

(db, client) = connect_to_db()

db_name = db.name

client.drop_database(db_name)
db = client[db_name]

index = db.create_collection('images')
index.create_index(['sourceId', 'source'], unique=True)
index.create_index(['originUrls'], unique=True, sparse=True)
index.create_index(['tags'])
index.create_index(['originMD5'])

tags = db.create_collection('tags')
tags.create_index(['sourceId', 'source'], unique=True)
tags.create_index(['count'])
tags.create_index(['category'])
tags.create_index(['originName', 'source'], unique=True)
tags.create_index(['v1Name'], unique=True)
tags.create_index(['v2Name'], unique=True)
tags.create_index(['v2Short'], unique=True)
tags.create_index(['preferredName'], unique=True)

implications = db.create_collection('implications')
implications.create_index(['originName'], unique=False)
implications.create_index(['sourceId', 'source'], unique=True)

translations = db.create_collection('translations')
translations.create_index(['sourceId', 'source'], unique=True)
translations.create_index(['originName', 'source'], unique=True)
translations.create_index(['e621Name'], unique=True)
