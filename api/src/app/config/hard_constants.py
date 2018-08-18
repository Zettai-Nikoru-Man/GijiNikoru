class HardConstants:
    """システム定数"""

    class App:
        ROOT = '/usr/src/app'
        TEMP_DIR = '/tmp/giji_nikoru'
        DB_DUMP_DIR_NAME = 'gijinikoru_data'
        DB_DUMP_DIR = '{}/{}'.format(TEMP_DIR, DB_DUMP_DIR_NAME)
        DB_DUMP_ZIP_NAME = '{}.zip'.format(DB_DUMP_DIR_NAME)
        DB_DUMP_ZIP = '{}/{}'.format(TEMP_DIR, DB_DUMP_ZIP_NAME)
        REPORT_CSV = '{}/report.csv'.format(DB_DUMP_DIR)
        DB_DUMP_SQL = '{}/dump.sql'.format(DB_DUMP_DIR)
        DB_EXPORT_SHELL = '{}/db_export.sh'.format(ROOT)
        NICORU_CSV_TO_BE_IMPORTED = '{}/nicoru_to_be_imported.csv'.format(TEMP_DIR)
        DB_DUMP_ZIP_PATH_ON_DROPBOX = '/{}'.format(DB_DUMP_ZIP_NAME)

    class Test:
        ROOT = '/usr/src/app'
        TEMP_DIR = '/tmp/test'
        DB_DUMP_DIR_NAME = 'gijinikoru_data'
        DB_DUMP_DIR = '{}/{}'.format(TEMP_DIR, DB_DUMP_DIR_NAME)
        DB_DUMP_ZIP_NAME = '{}.zip'.format(DB_DUMP_DIR_NAME)
        DB_DUMP_ZIP = '{}/{}'.format(TEMP_DIR, DB_DUMP_ZIP_NAME)
        REPORT_CSV = '{}/report.csv'.format(DB_DUMP_DIR)
        DB_DUMP_SQL = '{}/dump.sql'.format(DB_DUMP_DIR)
        DB_EXPORT_SHELL = '{}/test_db_export.sh'.format(ROOT)
        NICORU_CSV_TO_BE_IMPORTED = '{}/nicoru_to_be_imported.csv'.format(TEMP_DIR)
        DB_DUMP_ZIP_PATH_ON_DROPBOX = '/{}'.format(DB_DUMP_ZIP_NAME)
