from typing import Any, Callable, Optional, Tuple
import pandas as pd
from tiny_data_warehouse import DataWarehouse

tdw = DataWarehouse()


class BaseTable:
    table_name = None
    schema = None
    auth_context : Optional[Tuple[Callable, str]]= None

    def __init__(self):
        if not self.table_name:
            raise Exception("Table name is required")

    def read(self, recent_first=False):
        try:
            df = tdw.event(self.table_name)

            if self.auth_context:
                if self.auth_context[1] not in df.columns:
                    raise Exception("No authentication filter column found. Skipping filter")

                df = df[df[self.auth_context[1]] == self.auth_context[0]()]
                print("Filtered df with auth context")


            if recent_first:
                df = df.sort_values(by="tdw_timestamp", ascending=False)
        except ValueError:
            return pd.DataFrame(columns=self.schema.keys())

        return df

    def add(self, **kwargs) -> str:
        """
        Use like:
            .add(message=message, paper_url=paper.abstract_ur)
        """
        data = {}
        if self.auth_context:
            kwargs[self.auth_context[1]] = self.auth_context[0]()

        for key, metadata in self.schema.items():
            if key not in kwargs:
                raise Exception(f"Column {key} is required but not passed")

            data[key] = kwargs[key]


        return tdw.write_event(self.table_name, data)

    def len(self) -> int:
        return len(self.read().index)

    def load_with_value(self, column: str, value: Any, recent_first=False):
        df = self.read(recent_first=recent_first)
        return df[df[column] == value]

    def reset(self, dry_run=False):
        if dry_run:
            print("Dry run enabled exitting")
            return

        import pandas as pd

        df = pd.DataFrame()

        tdw.replace_df(self.table_name, df, dry_run=True)

    def replace(self, df, dry_run=True):
        tdw.replace_df(self.table_name, df, dry_run=dry_run)

    def is_empty(self) -> bool:
        return self.read().empty

    def update_or_create(self, by_key: str, by_value: Any, new_values: dict):
        # fix the new values using the key when missing
        if by_key not in new_values:
            new_values[by_key] = by_value

        df = self.read()
        if df.empty or df[df[by_key] == by_value].empty:
            self.add(**new_values)
        else:
            print(
                f"Row does exist for value {by_value}, updating row with values {new_values}"
            )
            # udpate the pandas rows that match the key with the new column values
            for column, new_value in new_values.items():
                df[column] = df.apply(
                    lambda row: new_value if row[by_key] == by_value else row[column],
                    axis=1,
                )

            tdw.replace_df(self.table_name, df, dry_run=False)

    def update(self, by_key: str, by_value: Any, new_values: dict):
        # fix the new values using the key when missing
        if by_key not in new_values:
            new_values[by_key] = by_value

        df = self.read()
        if df.empty or df[df[by_key] == by_value].empty:
            raise ValueError(f"Row does not exist for value {by_value}")
        else:
            print(
                f"Row does exist for value {by_value}, updating row with values {new_values}"
            )
            # udpate the pandas rows that match the key with the new column values
            for column, new_value in new_values.items():
                df[column] = df.apply(
                    lambda row: new_value if row[by_key] == by_value else row[column],
                    axis=1,
                )

            tdw.replace_df(self.table_name, df, dry_run=False)

    def delete_by(self, column: str, value: Any):
        df = self.read()
        df = df.reset_index(drop=True)

        df_dropped = df.drop(df[df[column] == value].index)
        tdw.replace_df(self.table_name, df_dropped)
        return True

    def last(self):
        return self.read().sort_values(by="tdw_timestamp", ascending=False).iloc[0]

    def print(self):
        df = self.read(recent_first=True)
        print(df)
