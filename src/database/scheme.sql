BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS "posts" (
 "post_id" INTEGER PRIMARY KEY,
 "text" TEXT,
 "time" DATETIME,
 "channel_id" INTEGER,
 "status" TEXT,
 PRIMARY KEY("post_id" AUTOINCREMENT),
);
CREATE TABLE IF NOT EXISTS "assortment" (
 "number" INTEGER PRIMARY KEY,
 "name" TEXT,
 "description" TEXT,
 "price" INTEGER,
 "priceDiscount" INTEGER,
 PRIMARY KEY("number" AUTOINCREMENT)
);
COMMIT;