import datetime
from state_of_the_art.tables.base_table import BaseTable


class PushHistory(BaseTable):
    table_name = "s3_push_history"
    schema = {}

    def get_last(self):
        return self.last().to_dict()["tdw_timestamp"]

    def minutes_since_last_push(self):
        now = datetime.datetime.now()
        last = self.get_last().to_pydatetime()
        return ((now - last).total_seconds()) / 60


if __name__ == "__main__":
    import fire

    fire.Fire()
