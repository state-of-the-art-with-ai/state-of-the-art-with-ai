from tiny_data_warehouse import DataWarehouse
tdw = DataWarehouse()


class BaseTable():
    table_name = None
    schema = None

    def __init__(self):
        if not self.schema:
            raise Exception("Schema is required")
        if not self.table_name:
            raise Exception("Table name is required")



    @classmethod
    def add(cls, **kwargs):
        data = {}
        for key, metadata in cls.schema.items():
            if key not in kwargs:
                raise Exception(f"Column {key} is required")

            data[key] = kwargs[key]

        tdw.write_event(cls.table_name, data)

    @classmethod
    def read(cls, recent_first=False):
        df = tdw.event(cls.table_name)

        if recent_first:
            df = df.sort_values(by='tdw_timestamp', ascending=False)


        return df
    
    @classmethod
    def len(cls) -> int:
        return len(cls.read().index)

    @classmethod
    def load_with_value(cls, column, value, recent_first=False):
        df = cls.read(recent_first=recent_first)
        return df[df[column] == value]

    @classmethod
    def delete_by(cls, column, value):
        df = cls.read()
        df = df.reset_index(drop=True)

        df_dropped = df.drop(df[df[column] == value].index)
        tdw.replace_df(cls.table_name, df_dropped, dry_run=False)
        return True