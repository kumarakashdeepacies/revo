import os

import environ
import psycopg2

from config.settings.base import get_tenants_map

env = environ.Env()

server = os.environ.get("POSTGRES_HOST", "172.22.16.1")
database = os.environ.get("POSTGRES_DB", "Platform_DB")
username = os.environ.get("POSTGRES_USER", "postgres")
password = os.environ.get("POSTGRES_PASSWORD", "postgres")
port = os.environ.get("POSTGRES_PORT", "5433")
database_type = os.environ.get("DATABASE_TYPE", "PostgreSQL")


sql_engine = psycopg2.connect(dbname=database, user=username, password=password, host=server, port=port)

tenants_data = get_tenants_map()
schemas_list = tenants_data.keys()
platform_admin = f"DROP Table IF EXISTS platform_admin.spirit_category_category, platform_admin.spirit_comment_bookmark_commentbookmark, platform_admin.spirit_comment_comment, platform_admin.spirit_comment_flag_commentflag, platform_admin.spirit_comment_flag_flag, platform_admin.spirit_user_userprofile, platform_admin.spirit_topic_topic, platform_admin.spirit_topic_unread_topicunread, platform_admin.spirit_comment_history_commenthistory, platform_admin.spirit_comment_like_commentlike, platform_admin.spirit_comment_poll_commentpoll, platform_admin.spirit_comment_poll_commentpollchoice, platform_admin.spirit_comment_poll_commentpollvote, platform_admin.spirit_topic_favorite_topicfavorite, platform_admin.spirit_topic_notification_topicnotification, platform_admin.spirit_topic_private_topicprivate cascade;"
cursor = sql_engine.cursor()
cursor.execute(platform_admin)
sql_engine.commit()
cursor.close()

for schema in schemas_list:
    query = f"DROP Table IF EXISTS {schema}.spirit_category_category, {schema}.spirit_comment_bookmark_commentbookmark, {schema}.spirit_comment_comment, {schema}.spirit_comment_flag_commentflag, {schema}.spirit_comment_flag_flag, {schema}.spirit_user_userprofile, {schema}.spirit_topic_topic, {schema}.spirit_topic_unread_topicunread, {schema}.spirit_comment_history_commenthistory, {schema}.spirit_comment_like_commentlike, {schema}.spirit_comment_poll_commentpoll, {schema}.spirit_comment_poll_commentpollchoice, {schema}.spirit_comment_poll_commentpollvote, {schema}.spirit_topic_favorite_topicfavorite, {schema}.spirit_topic_notification_topicnotification, {schema}.spirit_topic_private_topicprivate cascade;"
    query_admin = f"DROP Table IF EXISTS {schema}_admin.spirit_category_category, {schema}_admin.spirit_comment_bookmark_commentbookmark, {schema}_admin.spirit_comment_comment, {schema}_admin.spirit_comment_flag_commentflag, {schema}_admin.spirit_comment_flag_flag, {schema}_admin.spirit_user_userprofile, {schema}_admin.spirit_topic_topic, {schema}_admin.spirit_topic_unread_topicunread, {schema}_admin.spirit_comment_history_commenthistory, {schema}_admin.spirit_comment_like_commentlike, {schema}_admin.spirit_comment_poll_commentpoll, {schema}_admin.spirit_comment_poll_commentpollchoice, {schema}_admin.spirit_comment_poll_commentpollvote, {schema}_admin.spirit_topic_favorite_topicfavorite, {schema}_admin.spirit_topic_notification_topicnotification, {schema}_admin.spirit_topic_private_topicprivate cascade;"
    cursor = sql_engine.cursor()
    cursor.execute(query)
    cursor.execute(query_admin)
    sql_engine.commit()
    cursor.close()
