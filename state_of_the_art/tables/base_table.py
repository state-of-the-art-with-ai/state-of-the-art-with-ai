from typing import Any
import pandas as pd
from tiny_data_warehouse import DataWarehouse

tdw = DataWarehouse()


class BaseTable:
    table_name = None
    schema = None

    def __init__(self):
        if not self.table_name:
            raise Exception("Table name is required")

    @classmethod
    def add(cls, **kwargs):
        """
        Use like:
            .add(message=message, paper_url=paper.abstract_ur)
        """
        data = {}
        for key, metadata in cls.schema.items():
            if key not in kwargs:
                raise Exception(f"Column {key} is required")

            data[key] = kwargs[key]

        tdw.write_event(cls.table_name, data)

    @classmethod
    def read(cls, recent_first=False):
        try:
            df = tdw.event(cls.table_name)
            if recent_first:
                df = df.sort_values(by="tdw_timestamp", ascending=False)
        except ValueError:
            return pd.DataFrame(columns=cls.schema.keys())

        return df

    @classmethod
    def len(cls) -> int:
        return len(cls.read().index)

    @classmethod
    def load_with_value(cls, column: str, value: Any, recent_first=False):
        df = cls.read(recent_first=recent_first)
        return df[df[column] == value]

    def reset(cls, dry_run=False):
        if dry_run:
            print("Dry run enabled exitting")
            return

        import pandas as pd

        df = pd.DataFrame()

        tdw.replace_df(cls.table_name, df, dry_run=True)

    @classmethod
    def replace(cls, df, dry_run=True):
        tdw.replace_df(cls.table_name, df, dry_run=dry_run)

    @classmethod
    def is_empty(cls) -> bool:
        return cls.read().empty

    @classmethod
    def update_or_create(cls, by_key: str, by_value: Any, new_values: dict):
        # fix the new values using the key when missing
        if by_key not in new_values:
            new_values[by_key] = by_value

        df = cls.read()
        if cls.is_empty():
            filtered_df = df[df[by_key] == by_value]
            if filtered_df.empty:
                cls.add(**new_values)
        else:
            # udpate the pandas rows that match the key with the new column values
            for column, new_value in new_values.items():
                df[column] = df.apply(
                    lambda row: new_value if row[by_key] == by_value else row[column],
                    axis=1,
                )

            tdw.replace_df(cls.table_name, df, dry_run=False)

    @classmethod
    def delete_by(cls, column: str, value: Any):
        df = cls.read()
        df = df.reset_index(drop=True)

        df_dropped = df.drop(df[df[column] == value].index)
        tdw.replace_df(cls.table_name, df_dropped, dry_run=False)
        return True

    def last(cls):
        return cls.read().sort_values(by="tdw_timestamp", ascending=False).iloc[0]
