# SPDX-FileCopyrightText: 2026 Pirkka Toivakka
# SPDX-License-Identifier: Apache-2.0

import os
import psycopg

def connect_read():
    return psycopg.connect(
        host=os.environ['DB_HOST'],
        user=os.environ['DB_READ_USER'],
        password=os.environ['DB_READ_PASS'],
        port=os.environ['DB_PORT'],
        dbname=os.environ['DB_NAME'],
        autocommit=False,
        prepare_threshold=None
    )

def connect_write():
    return psycopg.connect(
        host=os.environ["DB_HOST"],
        user=os.environ["DB_WRITE_USER"],
        password=os.environ["DB_WRITE_PASS"],
        port=os.environ["DB_PORT"],
        dbname=os.environ["DB_NAME"],
        autocommit=True,
        prepare_threshold=None
    )