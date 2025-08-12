Class structure (modular, extensible)
DBConnector (core, required now)
Responsibility: centralize DB configuration and pooled connections for multiple environments (e.g., ingestion, app).

Key methods (signatures to finalize in Step 2):

__init__(ingestion: Optional[DBSettings], app: Optional[DBSettings], echo: bool=False)
get_engine(target: Literal["ingestion","app"]) -> Engine
connect(target="ingestion") -> contextmanager[Connection]
transaction(target="ingestion") -> contextmanager[Connection]
test_connection(target="ingestion") -> dict
execute(sql: str, params: dict|None=None, target="ingestion") -> int
fetch_df(sql: str, params: dict|None=None, target="ingestion") -> pd.DataFrame (optional but very handy)
to_sql(df: pd.DataFrame, table: str, schema: str|None=None, if_exists="append", target="ingestion") -> None
dispose_engine(target) / dispose_all()