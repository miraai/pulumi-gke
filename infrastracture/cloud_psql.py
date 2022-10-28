from pulumi import Config, export, Output
from pulumi_gcp.sql import DatabaseInstance, Database, DatabaseInstanceSettingsArgs, User

from infrastracture.consts import DEFAULT_LOCATION

config = Config()

def create_cloud_sql_instance(
    resource_name,
    database_version,
    database_name,
    database_tier = None,
    deletion_protection = None,
    database_password = None,
    region = DEFAULT_LOCATION,
):
    if not deletion_protection:
        deletion_protection = False

    if not database_tier:
        database_tier = "db-f1-micro"

    if not database_password:
        database_password=config.require_secret("database_password")

    cloud_sql_instance = DatabaseInstance(
        resource_name=resource_name,
        region=region,
        database_version=database_version,
        deletion_protection=deletion_protection,
        settings=DatabaseInstanceSettingsArgs(
            tier=database_tier,
        )
    )

    database = Database(
        "database",
        instance=cloud_sql_instance.name,
        name=database_name
    )

    users = User(
        "db_users",
        name=database_name,
        instance=cloud_sql_instance.name,
        password=database_password
    )

    sql_instance_url = Output.concat(
        "postgres://",
        database_name,
        ":",
        database_password,
        "@/",
        database_name,
        "?host=/cloudsql/",
        cloud_sql_instance.connection_name,
    )

    export("cloud_sql_instance_name", cloud_sql_instance.name)
    export("sql_instance_url", sql_instance_url)